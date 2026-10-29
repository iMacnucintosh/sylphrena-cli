{
  description = "CLI for Sylphrena Shell";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";

    caelestia-shell = {
      url = "github:caelestia-dots/shell";
      inputs.nixpkgs.follows = "nixpkgs";
      inputs.caelestia-cli.follows = "";
    };
  };

  outputs = {
    self,
    nixpkgs,
    ...
  } @ inputs: let
    inherit (nixpkgs.lib) genAttrs platforms lists systems;

    pkgsOf = nixpkgs.legacyPackages;
    systems' = lists.intersectLists platforms.linux systems.flakeExposed;
    eachSystem = genAttrs systems';
  in {
    formatter = eachSystem (system: pkgsOf.${system}.alejandra);

    packages = eachSystem (system: rec {
      sylphrena-cli = pkgsOf.${system}.callPackage ./default.nix {
        rev = self.rev or self.dirtyRev;
        caelestia-shell = inputs.caelestia-shell.packages.${system}.default;
      };
      with-shell = sylphrena-cli.override {withShell = true;};
      default = sylphrena-cli;
    });

    devShells = eachSystem (system: {
      default = pkgsOf.${system}.mkShellNoCC {
        packages = [self.packages.${system}.with-shell];
      };
    });
  };
}
