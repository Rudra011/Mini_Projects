namespace SyncVerseRGB.Core;

using System.Drawing;

public static class ColorUtils
{
    public static (byte r, byte g, byte b) ToBytes(Color c)
        => (c.R, c.G, c.B);

    public static Color Lerp(Color a, Color b, float t)
    {
        t = Math.Clamp(t, 0f, 1f);
        return Color.FromArgb(
            (byte)(a.R + (b.R - a.R) * t),
            (byte)(a.G + (b.G - a.G) * t),
            (byte)(a.B + (b.B - a.B) * t));
    }
}
