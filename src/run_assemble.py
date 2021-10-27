#!/usr/bin/env python

# SPDX-License-Identifier: Apache-2.0
#
# The OpenSearch Contributors require contributions made to
# this file be licensed under the Apache-2.0 license or a
# compatible open source license.

import argparse
import logging
import os
import sys

from assemble_workflow.bundle_recorder import BundleRecorder
from assemble_workflow.bundles import Bundles
from manifests.build_manifest import BuildManifest
from system import console
from system.temporary_directory import TemporaryDirectory


def main():
    parser = argparse.ArgumentParser(description="Assemble an OpenSearch Bundle")
    parser.add_argument("manifest", type=argparse.FileType("r"), help="Manifest file.")
    parser.add_argument(
        "-v",
        "--verbose",
        help="Show more verbose output.",
        action="store_const",
        default=logging.INFO,
        const=logging.DEBUG,
        dest="logging_level",
    )
    parser.add_argument("-b", "--base-url", dest='base_url', help="The base url to download the artifacts.")
    args = parser.parse_args()

    console.configure(level=args.logging_level)

    build_manifest = BuildManifest.from_file(args.manifest)
    build = build_manifest.build
    artifacts_dir = os.path.dirname(os.path.realpath(args.manifest.name))
    output_dir = os.path.join(os.getcwd(), "dist")
    os.makedirs(output_dir, exist_ok=True)

    with TemporaryDirectory(chdir=True):
        logging.info(f"Bundling {build.name} ({build.architecture}) on {build.platform} into {output_dir} ...")

        bundle_recorder = BundleRecorder(build, output_dir, artifacts_dir, args.base_url)

        bundle = Bundles.create(build_manifest, artifacts_dir, bundle_recorder)

        bundle.install_min()
        bundle.install_plugins()
        logging.info(f"Installed plugins: {bundle.installed_plugins}")

        #  Save a copy of the manifest inside of the tar
        bundle_recorder.write_manifest(bundle.archive_path)
        bundle.build_tar(output_dir)

        bundle_recorder.write_manifest(output_dir)

    logging.info("Done.")


if __name__ == "__main__":
    sys.exit(main())