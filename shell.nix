{
  pkgs ? import <nixpkgs> { },
}:
pkgs.mkShell {
  nativeBuildInputs = with pkgs.buildPackages; [
    ffmpeg
    python3
    (python3Packages.buildPythonPackage {
      pname = "ass";
      version = "0.5.4";
      src = pkgs.fetchPypi {
        pname = "ass";
        version = "0.5.4";
        sha256 = "sha256-ez2xkp2XUSGj5EnzjOd0e/qojqSqEgLNhMFPqF07pdA=";
      };
      doCheck = false;
    })
    (python3Packages.buildPythonPackage {
      pname = "srt";
      version = "3.5.3";
      src = pkgs.fetchPypi {
        pname = "srt";
        version = "3.5.3";
        sha256 = "sha256-SIQxUEOk8HQP0fh47WyqN2rAbXDhNfMGptxEYy7tDMA=";
      };
      doCheck = false;
    })
    (python3Packages.buildPythonPackage {
      pname = "ass_tag_parser";
      version = "2.4.1";
      src = pkgs.fetchPypi {
        pname = "ass_tag_parser";
        version = "2.4.1";
        sha256 = "sha256-H3i39vn2nnadn8h6l38JhlNLZfqBbEEBa4B5THhRAvc=";
      };
      doCheck = false;
    })
  ];

}
