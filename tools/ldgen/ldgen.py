#!/usr/bin/env python
#
# Copyright 2018-2019 Espressif Systems (Shanghai) PTE LTD
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import argparse
import os

from fragments import FragmentFileModel
from sdkconfig import SDKConfig
from generation import GenerationModel, TemplateModel, SectionsInfo

def main():

    argparser = argparse.ArgumentParser(description = "ESP-IDF linker script generator")

    argparser.add_argument(
        "--input", "-i",
        help = "Linker template file",
        type = argparse.FileType("r"))

    argparser.add_argument(
        "--fragments", "-f",
        type = argparse.FileType("r"),
        help = "Input fragment files",
        nargs = "+")

    argparser.add_argument(
        "--sections", "-s",
        type = argparse.FileType("r"),
        help = "Library sections info",
        nargs = "+")

    argparser.add_argument(
        "--output", "-o",
        help = "Output linker script",
        type = argparse.FileType("w"))

    argparser.add_argument(
        "--config", "-c",
        help = "Project configuration",
        type = argparse.FileType("r"))

    argparser.add_argument(
        "--kconfig", "-k",
        help = "IDF Kconfig file",
        type = argparse.FileType("r"))

    argparser.add_argument(
        "--env", "-e",
        action='append', default=[],
        help='Environment to set when evaluating the config file', metavar='NAME=VAL')

    args = argparser.parse_args()

    input_file = args.input
    fragment_files = [] if not args.fragments else args.fragments
    config_file = args.config
    output_file = args.output
    sections_info_files = [] if not args.sections else args.sections
    kconfig_file = args.kconfig
    
    try:
        sections_infos = SectionsInfo()

        for sections_info_file in sections_info_files:
            sections_infos.add_sections_info(sections_info_file)

        generation_model = GenerationModel()

        for fragment_file in fragment_files:
            fragment_file = FragmentFileModel(fragment_file)
            generation_model.add_fragments_from_file(fragment_file)

        sdkconfig = SDKConfig(kconfig_file, config_file, args.env)
        mapping_rules = generation_model.generate_rules(sdkconfig, sections_infos)

        script_model = TemplateModel(input_file)
        script_model.fill(mapping_rules, sdkconfig)

        script_model.write(output_file)

    except Exception, e:
        print("linker script generation failed for %s\nERROR: %s" % (input_file.name, e.message))
        # Delete the file so the entire build will fail; and not use an outdated script.
        os.remove(output_file.name)

if __name__ == "__main__":
    main()