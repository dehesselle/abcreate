# application bundle creator

`abcreate` is a CLI tool to create a macOS application bundle from executables, libraries and resource files in a given installation prefix directory. It takes its instructions from an XML based configuration file (see the [examples](examples)).

This tool was inspired by and built to replace [GTK Mac Bundler](https://gitlab.gnome.org/GNOME/gtk-mac-bundler) in my projects. Features and fixes will be developed as I go and to the extent as required for said projects. There are no plans to turn this into a general-purpose "swiss army knife" of packaging tools.

💁 _For the time being, this is to be considered "alpha" software. It works for the cases I need it to work._

## Features

- Require as little configuration as possible in a simple XML file that's easy to understand.
- Automatically pull in linked libraries.
- Automatically adjust library link paths in executables and libraries with relocatability in mind.
- Targeted towards GTK based apps (GTK versions 3 and 4), e.g. take care of pixbuf loaders, compile typelib files etc.  

## Installation

`abcreate` is on [PyPi](https://pypi.org/project/abcreate/), simply run:

```bash
pip install abcreate
```

## Usage

Let's look at an example:

```bash
abcreate create bundle.xml -s $HOME/install_prefix -t $HOME
```

- The first argument is a command. At the moment, there is only one command available, which is `create`.
- The `create` command expects
  - the name of a XML configuration file, e.g. `bundle.xml`
  - a source directory (`-s`) containing `bin`, `lib`, `share` etc. directories, i.e. the install prefix of the software you want to package
  - a target directory (`-t`) where the application bundle will be created in

## License

[GPL-2.0-or-later](LICENSE)
