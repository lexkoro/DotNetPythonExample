using System;
using System.IO;
using System.Linq;
using Python.Runtime;
using System.Collections.Generic;
using System.Diagnostics;
using System.Threading.Tasks;
using System.IO.Compression;

namespace DotNetPython
{

    public class Program
    {
        public static Lazy<PyScope> m_scope = new Lazy<PyScope>(() => Py.CreateScope());
        public static dynamic jobHandler;

        public static void ExecuteCommand(string command)
        {
            try
            {
                using (Py.GIL())
                {
                    var pyCompile = PythonEngine.Compile(command);
                    m_scope.Value.Execute(pyCompile);
                }
            }
            catch (Exception ex)
            {
                string result = $"Trace: \n{ex.StackTrace} " + "\n" +
                    $"Message: \n {ex.Message}" + "\n";
                Console.WriteLine(result);
            }
        }

        public static void initSynthesizer()
        {
            using (Py.GIL())
            {
                jobHandler = PyModule.Import("synth");

            }
        }

        public static void installDeps()
        {
            using (Py.GIL())
            {
                dynamic installer = PyModule.Import("installer");
                dynamic validate_function = installer.validate_deps;
                dynamic ret_value = validate_function();
                Console.WriteLine(ret_value);
            }
        }

        public static void SetSearchPath(IList<string> paths)
        {
            var searchPaths = paths.Where(Directory.Exists).Distinct().ToList();

            using (Py.GIL())
            {
                var src = "import sys\n" +
                           $"sys.path.extend({searchPaths.ToPython()})";
                ExecuteCommand(src);
            }
        }

        public static void Synthesize(int speakerID, string text)
        {
            using (Py.GIL())
            {

                dynamic process_task = jobHandler.process_task;
                process_task(speakerID, text);

            }
        }


        static void Main(string[] args)
        {

            // Extract the Embedded Python first
            var zipPath = Environment.CurrentDirectory + @"\PythonRuntime.zip";
            var extractPath = Environment.CurrentDirectory + @"\PythonRuntime";

            if (!Directory.Exists(extractPath))
            {
                ZipFile.ExtractToDirectory(zipPath, extractPath);
            }
            else
            {
                Console.WriteLine("{0} already Exists.", extractPath);
            }

            // Define Paths to the Python executable
            var pythonExecutable = Environment.CurrentDirectory + @"\PythonRuntime\python.exe";

            // Install python package manager "pip"
            var get_pip = Environment.CurrentDirectory + @"\PythonRuntime\get-pip.py";
            ProcessStartInfo processInfo = new ProcessStartInfo()
            {
                FileName = pythonExecutable,
                Arguments = get_pip,
                UseShellExecute = false,
                CreateNoWindow = true,
                RedirectStandardOutput = true

            };

            using (Process process = Process.Start(processInfo))
            {
                using (StreamReader reader = process.StandardOutput)
                {
                    string result = reader.ReadToEnd();
                    Console.Write(result);
                }
                process.WaitForExit();
            }

            // initiliaze python runtime 
            Runtime.PythonDLL = Environment.CurrentDirectory + @"\PythonRuntime\python38.dll";

            // start the python engine
            PythonEngine.Initialize();
            var m_threadState = PythonEngine.BeginAllowThreads();

            // set the path where python should search for our python scripts
            SetSearchPath(new List<string> { Environment.CurrentDirectory + @"\GameTTS\" });

            // here we import our python modules to call the functions directly from C#
            // first install dependencies
            installDeps();

            // initialize the synthesizer
            initSynthesizer();

            // we can now call the python synthesizer directly from C# and pass parameters to the function
            for (int idx = 0; idx < 3; idx++)
            {

                string text = "Ich bin mir leider nicht sicher, ob ich das gestern richtig verstanden habe.";
                Synthesize(idx, text);

            }

            Console.WriteLine("Press Any Key To Exit.");
            Console.ReadKey();
            // when closing the app also shutdown the python engine
            PythonEngine.EndAllowThreads(m_threadState);
            PythonEngine.Shutdown();


        }
    }
}
