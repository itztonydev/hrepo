{
  description = "hrepo - recursive Git submodule workspace orchestration";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils,
  }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = import nixpkgs {inherit system;};

      python = pkgs.python3;

      hrepo = python.pkgs.buildPythonApplication {
        pname = "hrepo";
        version = "0.1.0";

        pyproject = true;

        src = ./.;

        build-system = [python.pkgs.setuptools];

        dependencies = [];

        nativeCheckInputs = [pkgs.git];

        pythonImportsCheck = ["hrepo"];

        meta = {
          description = "Recursive Git submodule workspace orchestration";
          mainProgram = "hrepo";
          platforms = pkgs.lib.platforms.unix;
        };
      };
    in {
      packages = {
        default = hrepo;
        hrepo = hrepo;
      };

      apps.default = {
        type = "app";
        program = "${hrepo}/bin/hrepo";
      };

      devShells.default = pkgs.mkShell {
        packages = [python pkgs.git pkgs.gitMinimal];

        shellHook = ''echo "hrepo development environment" echo "Python: $(python --version)" echo "Git: $(git --version)" '';
      };
    });
}
