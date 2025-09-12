package com.mochasoft.portal.encrypt;

import java.text.DateFormat;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;
import java.util.GregorianCalendar;
import java.util.Locale;
import java.util.Random;

public class EncryptorUtil {
    private static int[] m_s1 = new int[] {
            18, 46, 52, 22, 39, 0, 58, 54, 23, 37, 
            38, 25, 42, 36, 62, 30, 41, 14, 7, 50, 
            8, 9, 51, 59, 21, 15, 34, 45, 56, 3, 
            55, 28, 49, 32, 35, 20, 24, 53, 33, 40, 
            11, 17, 26, 31, 48, 5, 43, 29, 44, 12, 
            1, 19, 4, 13, 16, 27, 57, 47, 2, 6, 
            63, 10, 61, 60 };

    private static int[] m_s2 = new int[] {
            5, 50, 58, 29, 52, 45, 59, 18, 20, 21,
            61, 40, 49, 53, 17, 25, 54, 41, 0, 51, 
            35, 24, 3, 8, 36, 11, 42, 55, 31, 47, 
            15, 43, 33, 38, 26, 34, 13, 9, 10, 4, 
            39, 16, 12, 46, 48, 27, 1, 57, 44, 32, 
            19, 22, 2, 37, 7, 30, 28, 56, 6, 23, 
            63, 62, 14, 60 };

    private static byte[] m = new byte[] {
            48, 49, 50, 51, 52, 53, 54, 55, 56, 57,
            65, 66,
            67, 68, 69, 70 };

    public static String getDateString() {
        DateFormat sdf1 = new SimpleDateFormat("yyyyMMddHHmmss", Locale.CHINESE);
        Calendar cal = GregorianCalendar.getInstance(Locale.CHINESE);
        Date date = cal.getTime();
        return sdf1.format(date);
    }

    public static boolean isValid(String sourceDate, int seconds) throws ParseException {
        DateFormat df = new SimpleDateFormat("yyyyMMddHHmmss", Locale.CHINESE);
        Date date = df.parse(sourceDate);
        Calendar cal = GregorianCalendar.getInstance(Locale.CHINESE);
        cal.setTime(date);
        cal.add(13, seconds);
        return cal.getTime().after(new Date());
    }

    public static String encode(String s, String s1) {
        String s2 = new StringBuffer(String.valueOf(s1)).append(":").append(getDateString()).toString();
        byte[] abyte0 = new byte[64];
        (new Random(System.currentTimeMillis())).nextBytes(abyte0);
        byte[] abyte1 = s2.getBytes();
        for (int i = 0; i < abyte1.length && i < 64; i++)
            abyte0[i] = abyte1[i];
        if (abyte1.length < 64)
            abyte0[abyte1.length] = 0;
        byte[] abyte2 = s.getBytes();
        for (int j = 0; j < abyte0.length; j++)
            abyte0[j] = (byte)(abyte0[j] + abyte2[j % abyte2.length]);
        return byteToString(switchArray(abyte0, m_s1));
    }

    public static String beforeDecode(String s, String s1) {
        byte[] abyte0 = switchArray(stringToByte(s1), m_s2);
        byte[] abyte1 = s.getBytes();
        for (int i = 0; i < abyte0.length; i++)
            abyte0[i] = (byte)(abyte0[i] - abyte1[i % abyte1.length]);
        int j = 64;
        int k = 0;
        while (k < 64 && k < abyte0.length) {
            if (abyte0[k] == 0) {
                j = k;
                break;
            }
            k++;
        }
        return new String(abyte0, 0, Math.min(j, abyte0.length));
    }

    public static String decode(String s, String s1, int seconds) throws ParseException {
        String result = beforeDecode(s, s1);
        String[] arr = result.split(":");
        if (isValid(arr[1], seconds))
            return arr[0];
        return null;
    }

    private static byte[] switchArray(byte[] abyte0, int[] ai) {
        byte[] abyte1 = new byte[abyte0.length];
        for (int i = 0; i < abyte1.length; i++)
            abyte1[i] = abyte0[ai[i]];
        return abyte1;
    }

    private static String byteToString(byte[] abyte0) {
        if (abyte0 == null || abyte0.length == 0)
            return "";
        byte[] abyte1 = new byte[2 * abyte0.length];
        for (int i = 0; i < abyte0.length; i++) {
            abyte1[2 * i + 0] = m[abyte0[i] & 0xF];
            abyte1[2 * i + 1] = m[(abyte0[i] & 0xF0) >> 4];
        }
        return new String(abyte1);
    }

    private static byte[] stringToByte(String s) {
        if (s == null || s.length() != 128)
            throw new IllegalArgumentException();
        byte[] abyte0 = new byte[64];
        for (int i = 0; i < 64; i++) {
            byte byte0 = 0;
            char c = s.charAt(2 * i + 0);
            char c1 = s.charAt(2 * i + 1);
            if (c >= '0' && c <= '9') {
                byte0 = (byte)(byte0 + c - 48);
            } else if (c >= 'A' && c <= 'F') {
                byte0 = (byte)(byte0 + c - 65 + 10);
            } else {
                throw new IllegalArgumentException();
            }
            if (c1 >= '0' && c1 <= '9') {
                byte0 = (byte)(byte0 + (c1 - 48) * 16);
            } else if (c1 >= 'A' && c1 <= 'F') {
                byte0 = (byte)(byte0 + (c1 - 65 + 10) * 16);
            } else {
                throw new IllegalArgumentException();
            }
            abyte0[i] = byte0;
        }
        return abyte0;
    }

    public static void main(String[] args) {
        try {
            // Test 1: Current algorithm test
            System.out.println("测试加密和解密: ");
            testEncryptDecrypt("admin", "SIMBEST_SSO");
            testEncryptDecrypt("qinfumin", "SIMBEST_SSO");
            testEncryptDecrypt("wangyikang", "SIMBEST_SSO");

            // Test 2: Hardcoded string test
            System.out.println();
            System.out.println("测试直接解密: ");
            String result = decode("SIMBEST_SSO", "49494E986A4C5375944CDEE19876243AFDB7DCE6D858D3421867CA98928A2F52EE4F608808A0EA9558583D01560C206D53E72B38ABD738CD6D0EBBDB7FF77C53", 1800);
            System.out.println( result);
        } catch (Exception e) {
            System.out.println("Exception: " + e.getMessage());
            e.printStackTrace();
        }
    }
    
    private static void testEncryptDecrypt(String originalText, String key) throws Exception {
        System.out.println("\n--- Test: '" + originalText + "' with key '" + key + "' ---");
        
        // Test encryption
        String encoded = encode(key, originalText);
        System.out.println("Encoded: " + encoded);
        
        // Test decryption
        String decoded = decode(key, encoded, 1800);
        System.out.println("Decoded: " + decoded);
        
        // Verify result
        if (originalText.equals(decoded)) {
            System.out.println("Result: PASSED");
        } else {
            System.out.println("Result: FAILED (expected: '" + originalText + "', got: '" + decoded + "')");
        }
    }
}
