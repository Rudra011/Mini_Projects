// SyncVerseRGB/Drivers/MsiM99DriverNative.cs
using System;
using System.Runtime.InteropServices;

namespace SyncVerseRGB.Drivers
{
    internal static class NativeMethods
    {
        [DllImport("kernel32", SetLastError = true, CharSet = CharSet.Unicode)]
        public static extern IntPtr LoadLibraryW(string lpFileName);

        [DllImport("kernel32", SetLastError = true, CharSet = CharSet.Ansi)]
        public static extern IntPtr GetProcAddress(IntPtr hModule, string procName);

        [DllImport("kernel32", SetLastError = true)]
        public static extern bool FreeLibrary(IntPtr hModule);

        // For calling by ordinal
        [DllImport("kernel32", SetLastError = true)]
        public static extern IntPtr GetModuleHandle(string lpModuleName);

        // Utility to marshal function pointer to delegate
        public static T GetDelegate<T>(IntPtr p) where T : Delegate
        {
            return (T)Marshal.GetDelegateForFunctionPointer(p, typeof(T));
        }
    }
}
