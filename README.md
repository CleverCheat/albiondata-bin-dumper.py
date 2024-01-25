# albiondata-bin-dumper.py
Decrypts Albion Online files, extracts data, and organizes into readable formats

## Installation

Before starting the installation, make sure you have Python 3.10 or a later version installed on your system. Then, follow the steps below:

1. Install PDM by following the instructions available on [the official PDM website](https://pdm-project.org/latest/#recommended-installation-method).

2. Run the following command to install the project dependencies:

   ```bash
   pdm install
    ```

3. After installation is complete, execute the following command to start:

   ```bash
   pdm run decrypt
    ```

    Optionally, you can add the base directory as an argument to the decrypt command using either **-d** or **--main-game-folder**:

   ```bash
   pdm run decrypt -d <path_to_base_directory>
    ```

    or


   ```bash
   pdm run decrypt --main-game-folder <path_to_base_directory>
    ```

    Replace <path_to_base_directory> with the absolute path of the directory to traverse.

## Disclaimer

This code is purely for fun, and I am aware that it might not be the best-written code. If someone messes up with this code, I cannot be held responsible for any consequences.

## License

This project is licensed under the MIT License - see the LICENSE file for details