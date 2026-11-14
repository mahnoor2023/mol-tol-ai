# Third-party notices

The Python SDK uses Python standard-library modules at runtime and includes no third-party runtime package. Its optional source-build backend declares `setuptools>=68`; this is a build-time dependency and is not bundled in the generated SDK wheel. The offline wheel builder uses only the Python standard library.

The static site uses local HTML, CSS, and an original Mol-Tol SVG mark. It loads no external font, script, image, analytics, or UI package.

Before distributing any additional artifact, review its exact dependencies and preserve applicable license texts and attributions. The repository retains its All rights reserved notice; no open-source license is granted here.