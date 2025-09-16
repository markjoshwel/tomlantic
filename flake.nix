{
  description = "develop or build/package tomlantic";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    nixpkgs24.url = "github:NixOS/nixpkgs/nixos-24.05";
    flake-utils.url = "github:numtide/flake-utils";

    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    uv2nix = {
      url = "github:pyproject-nix/uv2nix";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    pyproject-build-systems = {
      url = "github:pyproject-nix/build-system-pkgs";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.uv2nix.follows = "uv2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs =
    {
      nixpkgs,
      nixpkgs24,
      uv2nix,
      pyproject-nix,
      pyproject-build-systems,
      flake-utils,
      ...
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        inherit (nixpkgs) lib;
        pkgs = nixpkgs.legacyPackages.${system};
        pkgs24 = nixpkgs24.legacyPackages.${system};

        # create package overlay from workspace/project
        workspace = uv2nix.lib.workspace.loadWorkspace { workspaceRoot = ./.; };
        overlay = workspace.mkPyprojectOverlay { sourcePreference = "wheel"; };

        # extend generated overlay with build fixups
        pyprojectOverrides = _final: _prev: {
          # https://pyproject-nix.github.io/uv2nix/overriding/index.html
        };

        # construct package set
        python = pkgs.python313;
        pythonSet =
          # use base package set from pyproject.nix builders
          (pkgs.callPackage pyproject-nix.build.packages {
            inherit python;
          }).overrideScope
            (
              lib.composeManyExtensions [
                pyproject-build-systems.overlays.default
                overlay
                pyprojectOverrides
              ]
            );
      in
      {
        # nix develop [.#impure]
        devShells = {
          # it is of course perfectly OK to keep using an impure virtualenv workflow and only use uv2nix to build packages
          # this devShell simply adds Python and undoes the dependency leakage done by Nixpkgs Python infrastructure
          impure = pkgs.mkShell {
            packages = [
              python
              pkgs.uv
            ];
            env =
              {
                # prevent uv from managing python downloads
                UV_PYTHON_DOWNLOADS = "never";
                UV_PYTHON = python.interpreter;
              }
              // lib.optionalAttrs pkgs.stdenv.isLinux {
                LD_LIBRARY_PATH = lib.makeLibraryPath pkgs.pythonManylinuxPackages.manylinux1;
              };
            shellHook = ''
              unset PYTHONPATH
            '';
          };

          default =
            let
              editableOverlay = workspace.mkEditablePyprojectOverlay { root = "$REPO_ROOT"; };

              # override previous set with our overrideable overlay.
              editablePythonSet = pythonSet.overrideScope (
                lib.composeManyExtensions [
                  editableOverlay

                  # apply fixups for building an editable package of your workspace packages
                  (final: prev: {
                    hello-world = prev.hello-world.overrideAttrs (old: {
                      # it's a good idea to filter the sources going into an editable build
                      # so the editable package doesn't have to be rebuilt on every change.
                      src = lib.fileset.toSource {
                        root = old.src;
                        fileset = lib.fileset.unions [
                          (old.src + "/pyproject.toml")
                          (old.src + "/README.md")
                          (old.src + "/tomlantic/__init__.py")
                        ];
                      };

                      # hatchling (our build system) has a dependency on the `editables` package when building editables
                      #
                      # in normal Python flows, this dependency is dynamically handled, and doesn't need to be explicitly declared.
                      # this behaviour is documented in PEP-660
                      #
                      # with Nix the dependency needs to be explicitly declared
                      nativeBuildInputs = old.nativeBuildInputs ++ final.resolveBuildSystem { editables = [ ]; };
                    });

                  })
                ]
              );

              # build virtual environment, with local packages being editable with all optional dependencies
              virtualenv = editablePythonSet.mkVirtualEnv "tomlantic-dev-env" workspace.deps.all;

            in
            pkgs.mkShell {
              packages = [
                virtualenv
                pkgs.uv
              ];

              env = {
                UV_PYTHON = python.interpreter;
                # uv: don't create venvs
                UV_NO_SYNC = "1";
                # uv: don't manage/download python
                UV_PYTHON_DOWNLOADS = "never";
              };

              shellHook = ''
                unset PYTHONPATH
                export REPO_ROOT=$(git rev-parse --show-toplevel)
              '';
            };
        };

        # nix flake check
        checks =
          let
            test-virtualenv = pythonSet.mkVirtualEnv "tomlantic-testing-env" workspace.deps.all;
          in
          {
            tests =
              pkgs.runCommandLocal "tomlantic-check-tests"
                {
                  src = ./.;
                  buildInputs = [
                    test-virtualenv
                    pkgs.python313
                  ];
                }
                ''
                  cd ${./.}
                  python tests/test.py
                  mkdir -p $out
                '';
          };

        # package a virtual environment as our main application with no optional dependencies
        packages.default = pythonSet.mkVirtualEnv "tomlantic-env" workspace.deps.default;

        # nix run .#tests
        apps.tests =
          let
            makePythonSet =
              python:
              (pkgs.callPackage pyproject-nix.build.packages {
                inherit python;
              }).overrideScope
                (
                  lib.composeManyExtensions [
                    pyproject-build-systems.overlays.default
                    overlay
                    pyprojectOverrides
                  ]
                );

            pythonVersions = {
              "39" = pkgs24.python39;
              "310" = pkgs.python310;
              "311" = pkgs.python311;
              "312" = pkgs.python312;
              "313" = pkgs.python313;
              # "314" = pkgs.python314; (too new for pydantic wheels, oct 7)
            };

            venvs = lib.mapAttrs (
              k: py: (makePythonSet py).mkVirtualEnv "tomlantic-testing-env-${k}" workspace.deps.all
            ) pythonVersions;

            venvArgs = lib.concatStringsSep " " (lib.mapAttrsToList (k: v: ''"${k}=${v}/bin/python3"'') venvs);

            runner = pkgs.writeShellApplication {
              name = "tomlantic-tests";
              runtimeInputs = builtins.attrValues venvs;
              text = ''
                set -euo pipefail
                cd ${./.}
                ${venvs."313"}/bin/python3 tests/test.py ${venvArgs}
              '';
            };
          in
          {
            type = "app";
            program = "${runner}/bin/tomlantic-tests";
          };

        # nix run .#lint
        apps.lint =
          let
            linting-virtualenv = pythonSet.mkVirtualEnv "tomlantic-linting-env" workspace.deps.all;
            runner = pkgs.writeShellApplication {
              name = "tomlantic-lint";
              runtimeInputs = [ linting-virtualenv ];
              text = ''
                set -uo pipefail

                # because the project directory is read-only whilst ran here
                # wacky hack around nix and variables in strings
                TMPDIR="''${TMPDIR:-/tmp}"
                export TMPDIR

                export XDG_CACHE_HOME="$TMPDIR/xdg-cache"
                export RUFF_CACHE_DIR="$TMPDIR/ruff-cache"
                export MYPY_CACHE_DIR="$TMPDIR/mypy-cache"

                cd ${./.}
                ruff check tomlantic tests showcase.py
                ruff format --check tomlantic tests showcase.py
                isort --check tomlantic tests showcase.py
                mypy tomlantic tests showcase.py
              '';
            };
          in
          {
            type = "app";
            program = "${runner}/bin/tomlantic-lint";
          };
      }
    );
}
