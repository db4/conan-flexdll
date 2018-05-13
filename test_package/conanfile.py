from conans import ConanFile, CMake, tools


class flexdllTestConan(ConanFile):
    settings = "os", "compiler", "arch"
    generators = "compiler_args"

    def build(self):
        url = "https://github.com/alainfrisch/flexdll.git"
        self.run("git clone " + url)

        def compile(file):
            if self.settings.compiler == "Visual Studio":
                compile = "cl -c -Fo{0}.obj flexdll/test/{0}.c @conanbuildinfo.args"
            else:
                compile = "gcc -c -o {0}.o flexdll/test/{0}.c @conanbuildinfo.args"
            self.run(compile.format(file))

        def link(file, files, extra_opts=""):
            suffix = "64" if self.settings.arch == "x86_64" else ""
            if self.settings.compiler == "Visual Studio":
                chain = "msvc"
                files_str = " ".join([f+".obj" for f in files])
            else:
                chain = "mingw"
                files_str = " ".join([f+".o" for f in files])
            chain += suffix
            flexlink = "flexlink.exe -chain {0} -merge-manifest {1} -o {2} {3}"
            self.run(flexlink.format(chain, extra_opts, file, files_str))

        def compile_link():
            compile("dump")
            compile("plug1")
            compile("plug2")
            link("dump.exe", ["dump"], "-exe")
            link("plug1.dll", ["plug1"])
            link("plug2.dll", ["plug2"])

        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self.settings):
                compile_link()
        else:
            compile_link()

    def test(self):
        self.run("dump plug1.dll plug2.dll")
