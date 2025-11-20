// SyncVerseRGB/Drivers/MsiM99DriverWrapper.cs
using System;
using System.Runtime.InteropServices;

namespace SyncVerseRGB.Drivers
{
    public sealed class MsiM99DriverWrapper : IDisposable
    {
        private IntPtr _dll = IntPtr.Zero;

        // Delegates for exported functions
        private Set_VIDPID_Delegate? _setVidPid;
        private Open_ReportDevice_Delegate? _openReport;
        private Close_ReportDevice_Delegate? _closeReport;
        private WriteUSB_Delegate? _writeUsb;

        public string LoadedPath { get; private set; } = string.Empty;

        private static class NativeMethods
        {
            [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
            public static extern IntPtr LoadLibraryW(string lpLibFileName);

            [DllImport("kernel32.dll", SetLastError = true)]
            public static extern bool FreeLibrary(IntPtr hModule);

            [DllImport("kernel32.dll", SetLastError = true)]
            public static extern IntPtr GetProcAddress(IntPtr hModule, string procName);
        }

        [UnmanagedFunctionPointer(CallingConvention.StdCall)]
        private delegate bool Set_VIDPID_Delegate(ushort vid, ushort pid);

        [UnmanagedFunctionPointer(CallingConvention.StdCall)]
        private delegate bool Open_ReportDevice_Delegate();

        [UnmanagedFunctionPointer(CallingConvention.StdCall)]
        private delegate void Close_ReportDevice_Delegate();

        [UnmanagedFunctionPointer(CallingConvention.StdCall)]
        private delegate int WriteUSB_Delegate(byte[] buffer, int length);


        public void Load(string path)
        {
            if (_dll != IntPtr.Zero)
                return;

            Console.WriteLine("[M99] LoadLibraryW: " + path);

            _dll = NativeMethods.LoadLibraryW(path);
            if (_dll == IntPtr.Zero)
            {
                throw new Exception("Failed to load MSDriver.dll (LoadLibrary returned null).");
            }

            LoadedPath = path;

            // Required vendor functions
            _setVidPid  = LoadFunction<Set_VIDPID_Delegate>("Set_VIDPID");
            _openReport = LoadFunction<Open_ReportDevice_Delegate>("Open_ReportDevice");
            _closeReport = LoadFunction<Close_ReportDevice_Delegate>("Close_ReportDevice");
            _writeUsb   = LoadFunction<WriteUSB_Delegate>("WriteUSB");

            Console.WriteLine("[M99] All vendor functions loaded.");
        }


        private T LoadFunction<T>(string name) where T : Delegate
        {
            IntPtr proc = NativeMethods.GetProcAddress(_dll, name);
            if (proc == IntPtr.Zero)
                throw new Exception("GetProcAddress failed for " + name);

            return Marshal.GetDelegateForFunctionPointer<T>(proc);
        }


        public bool SetVidPid(ushort vid, ushort pid)
        {
            return _setVidPid != null && _setVidPid(vid, pid);
        }

        public bool OpenReport()
        {
            return _openReport != null && _openReport();
        }

        public void CloseReport()
        {
            _closeReport?.Invoke();
        }


        public bool WriteUSB(byte[] buffer)
        {
            if (_writeUsb == null)
                return false;

            // IMPORTANT: MSI driver expects EXACT 64 bytes
            return _writeUsb(buffer, 64) != 0;
        }


        public void Dispose()
        {
            try
            {
                _closeReport?.Invoke();

                if (_dll != IntPtr.Zero)
                {
                    NativeMethods.FreeLibrary(_dll);
                    _dll = IntPtr.Zero;
                }
            }
            catch { }
        }
    }
}
