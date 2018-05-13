import os
from conans import ConanFile, tools
from conans.model.version import Version

class flexdllConan(ConanFile):
    name = "flexdll"
    version = "0.37"
    settings = {"os": ["Windows"], "compiler": None, "arch": None, "build_type": None}
    generators = "compiler_args"
    description = "FlexDLL: an implementation of a dlopen-like API for Windows"
    license = "zlib/libpng license"
    url = "https://github.com/alainfrisch/flexdll"

    def configure(self):
        del self.settings.compiler.libcxx

    @property
    def vs15_or_newer(self):
        return self.settings.compiler == "Visual Studio" and Version(str(self.settings.compiler.version)) >= "15"

    def build(self):
        tools.get("https://github.com/alainfrisch/flexdll/releases/download/0.37/flexdll-bin-0.37.zip",
                  sha1="73494474c546992635c0b320ee519f103b56dd58")
        if self.vs15_or_newer:
            os.unlink("flexdll_msvc.obj")
            os.unlink("flexdll_msvc64.obj")
            os.unlink("flexdll_initer_msvc.obj")
            os.unlink("flexdll_initer_msvc64.obj")
            if self.settings.arch == "x86_64":
                compile = "cl -c -DMSVC -DMSVC64 -Fo{0}_msvc64.obj {0}.c @conanbuildinfo.args"
            else:
                compile = "cl -c -DMSVC -Fo{0}_msvc.obj {0}.c @conanbuildinfo.args"
            with tools.vcvars(self.settings):
                self.run(compile.format("flexdll"))
                self.run(compile.format("flexdll_initer"))

    def package(self):
        self.copy("*", dst="flexdll")

    def package_info(self):
        flexdll_dir = os.path.join(self.package_folder, "flexdll")
        self.cpp_info.includedirs.append(flexdll_dir)
        self.env_info.path.append(flexdll_dir)

    def package_id(self):
        if not self.vs15_or_newer:
            del self.info.settings.compiler
            del self.info.settings.arch
            del self.info.settings.build_type
