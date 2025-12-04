package org.jeecg.common.util;

import cn.hutool.core.codec.Base64Decoder;
import cn.hutool.core.codec.Base64Encoder;

import javax.crypto.Cipher;
import java.security.*;
import java.security.interfaces.RSAPrivateKey;
import java.security.interfaces.RSAPublicKey;
import java.security.spec.InvalidKeySpecException;
import java.security.spec.PKCS8EncodedKeySpec;
import java.security.spec.X509EncodedKeySpec;

/**
 * 创建 RSA 工具类 RSAUtils 和 access_token 签名
 */
public class RSAUtils {

    /**
     * 公钥
     */
    public static final String publicKeyBase64Default = "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC+K3y4fL71dFhFYC9c9bea9wPHyouU86VI0nI1GtDiMbSd3/mFcf/Z14hixordW8W8Q0BftncjcbIOHOeHDK074hpVbMdJTgadisuksX1fISp5CXa5ETsDcHa6usb1wGd2EFSo8ws5Jfi5oGZVgRzF3YLIKgxYn+NZu7cvHOD0GwIDAQAB";

    /**
     * 私钥
     */
    public static final String privateKeyBase64Default = "MIICeAIBADANBgkqhkiG9w0BAQEFAASCAmIwggJeAgEAAoGBAL4rfLh8vvV0WEVgL1z1t5r3A8fKi5TzpUjScjUa0OIxtJ3f+YVx/9nXiGLGit1bxbxDQF+2dyNxsg4c54cMrTviGlVsx0lOBp2Ky6SxfV8hKnkJdrkROwNwdrq6xvXAZ3YQVKjzCzkl+LmgZlWBHMXdgsgqDFif41m7ty8c4PQbAgMBAAECgYAD3jSSOA9WRMCK4LL17BWI9F9CUA9Yvz/sZENoaxw2jZZD48taeIAguS6P+8PVTsmN07xadgakVOqvOM1IxOw9E5kU9ygoZyx6+sTvn9Kw8lEQMh22JCwWkmDpg8ZZoNTczBjkzfTk8snNSLxzhfyYAAeRZsVClCeksBLG/SgCkQJBAOCnIn80nOaHBEiBxaW9FlmJsk1vAyLfdQ0MrP+14Q3WcZZlgX26FMh/KIAuoz37dI6fd3dl5F7xa0frZMnb8yMCQQDYtJRAIUHyLfLlvNUbDep7kzwKmHcnWhGo17vJTeH2Q+Ku/7Bqz+l3pDAJzHvUGpk02jTJL1E4pPNO1WF6lOapAkEA2LiDsAGah02jFSuT92Klh/UtPEQm22KEsfUTg4/7L3U7mOINfLOhzxXUhWv4cRf+hoRSJK34FJuDahss3QtBzwJBAMTCiU0FJWxwHfhMkS4EX6AeWkjAkIexdxFX+BBaX82La9o7HIKPDstrz5ZGDTTThcIAUidNiDCnTKeKhPyZECkCQQDAAls+KWcxt2DDaQr1nfOwMG+osLfhSW95YcBXqHKo8KdMIktJUkJBS8KwNF3/nrTj+GLL53yTPk1ckXXzkaQC";

    /**
     * 数字签名，密钥算法
     */
    private static final String RSA_KEY_ALGORITHM = "RSA";

    /**
     * 数字签名签名/验证算法
     */
    private static final String SIGNATURE_ALGORITHM = "MD5withRSA";

    /**
     * 公钥 key
     */
    private static final String PUBLIC_KEY = "RSAPublicKey";

    /**
     * 私钥 key
     */
    private static final String PRIVATE_KEY = "RSAPrivateKey";

    /**
     * RSA密钥长度，RSA算法的默认密钥长度是1024密钥长度必须是64的倍数，在512到65536位之间
     */
    private static final int KEY_SIZE = 1024;




    /**
     *
     * @param data   加密前的字符串
     * @param publicKey 公钥
     * @return 加密后的字符串
     * @throws Exception
     * @date    2023/10/5-23:49
     * @version 1.0
     * @description  公钥加密
     */
    public static String encryptByPubKey(String data, String publicKey) throws Exception {
        byte[] pubKey = Base64Decoder.decode(publicKey);
        byte[] enSign = encryptByPubKey(data.getBytes(), pubKey);
        return Base64Encoder.encode(enSign);
    }

    /**
     *
     * @param data 待加密数据
     * @param pubKey 公钥
     * @return
     * @throws Exception
     * @date    2023/10/5-23:49
     * @version 1.0
     * @description  公钥加密
     */
    public static byte[] encryptByPubKey(byte[] data, byte[] pubKey) throws Exception {
        X509EncodedKeySpec x509KeySpec = new X509EncodedKeySpec(pubKey);
        KeyFactory keyFactory = KeyFactory.getInstance(RSA_KEY_ALGORITHM);
        PublicKey publicKey = keyFactory.generatePublic(x509KeySpec);
        Cipher cipher = Cipher.getInstance(keyFactory.getAlgorithm());
        cipher.init(Cipher.ENCRYPT_MODE, publicKey);
        return cipher.doFinal(data);
    }

    /**
     *
     * @param text   加密前的字符串
     * @param privateKey 私钥
     * @return 加密后的字符串
     * @date    2023/10/5-23:48
     * @version 1.0
     * @description  私钥加密
     */
    public static String encryptByPriKey(String text, String privateKey) {
        try {
            byte[] priKey = Base64Decoder.decode(privateKey);
            byte[] enSign = encryptByPriKey(text.getBytes(), priKey);
            return Base64Encoder.encode(enSign);
        } catch (Exception e) {
            throw new RuntimeException("加密字符串[" + text + "]时遇到异常", e);
        }
    }

    /**
     *
     * @param data 待加密的数据
     * @param priKey 私钥
     * @return 加密后的数据
     * @throws Exception
     * @date    2023/10/5-23:48
     * @version 1.0
     * @description  私钥加密
     */
    public static byte[] encryptByPriKey(byte[] data, byte[] priKey) throws Exception {
        PKCS8EncodedKeySpec pkcs8KeySpec = new PKCS8EncodedKeySpec(priKey);
        KeyFactory keyFactory = KeyFactory.getInstance(RSA_KEY_ALGORITHM);
        PrivateKey privateKey = keyFactory.generatePrivate(pkcs8KeySpec);
        Cipher cipher = Cipher.getInstance(keyFactory.getAlgorithm());
        cipher.init(Cipher.ENCRYPT_MODE, privateKey);
        return cipher.doFinal(data);
    }

    /**
     *
     * @param data 待解密的数据
     * @param pubKey 公钥
     * @return 解密后的数据
     * @throws Exception
     * @date    2023/10/5-23:47
     * @version 1.0
     * @description  公钥解密
     */
    public static byte[] decryptByPubKey(byte[] data, byte[] pubKey) throws Exception {
        X509EncodedKeySpec x509KeySpec = new X509EncodedKeySpec(pubKey);
        KeyFactory keyFactory = KeyFactory.getInstance(RSA_KEY_ALGORITHM);
        PublicKey publicKey = keyFactory.generatePublic(x509KeySpec);
        Cipher cipher = Cipher.getInstance(keyFactory.getAlgorithm());
        cipher.init(Cipher.DECRYPT_MODE, publicKey);
        return cipher.doFinal(data);
    }

    /**
     *
     * @param data    解密前的字符串
     * @param publicKey 公钥
     * @return 解密后的字符串
     * @throws Exception
     * @date    2023/10/5-23:47
     * @version 1.0
     * @description  公钥解密
     */
    public static String decryptByPubKey(String data, String publicKey) throws Exception {
        byte[] pubKey = Base64Decoder.decode(publicKey);;
        byte[] design = decryptByPubKey(Base64Decoder.decode(data), pubKey);
        return new String(design);
    }

    /**
     *
     * @param data 待解密的数据
     * @param priKey 私钥
     * @return
     * @throws Exception
     * @date    2023/10/5-23:46
     * @version 1.0
     * @description  私钥解密
     */
    public static byte[] decryptByPriKey(byte[] data, byte[] priKey) throws Exception {
        PKCS8EncodedKeySpec pkcs8KeySpec = new PKCS8EncodedKeySpec(priKey);
        KeyFactory keyFactory = KeyFactory.getInstance(RSA_KEY_ALGORITHM);
        PrivateKey privateKey = keyFactory.generatePrivate(pkcs8KeySpec);
        Cipher cipher = Cipher.getInstance(keyFactory.getAlgorithm());
        cipher.init(Cipher.DECRYPT_MODE, privateKey);
        return cipher.doFinal(data);
    }

    /**
     *
     * @param secretText 解密前的字符串
     * @param privateKey 私钥
     * @return 解密后的字符串
     * @date    2023/10/5-23:46
     * @version 1.0
     * @description  私钥解密
     */
    public static String decryptByPriKey(String secretText, String privateKey) {
        try {
            byte[] priKey = Base64Decoder.decode(privateKey);;
            byte[] design = decryptByPriKey(Base64Decoder.decode(secretText), priKey);
            return new String(design);
        } catch (Exception e) {
            throw new RuntimeException("解密字符串[" + secretText + "]时遇到异常", e);
        }
    }

    /**
     *
     * @param data 待签名数据
     * @param priKey 私钥
     * @return 签名
     * @throws Exception
     * @date    2023/10/5-23:45
     * @version 1.0
     * @description  RSA签名
     */
    public static String sign(byte[] data, byte[] priKey) throws Exception {
        // 取得私钥
        PKCS8EncodedKeySpec pkcs8KeySpec = new PKCS8EncodedKeySpec(priKey);
        KeyFactory keyFactory = KeyFactory.getInstance(RSA_KEY_ALGORITHM);
        // 生成私钥
        PrivateKey privateKey = keyFactory.generatePrivate(pkcs8KeySpec);
        // 实例化Signature
        Signature signature = Signature.getInstance(SIGNATURE_ALGORITHM);
        // 初始化Signature
        signature.initSign(privateKey);
        // 更新
        signature.update(data);
        return Base64Encoder.encode(signature.sign());
    }


    /**
     *
     * @param data 待校验数据
     * @param sign 数字签名
     * @param pubKey 公钥
     * @return boolean 校验成功返回true，失败返回false
     * @throws Exception
     * @date    2023/10/5-23:44
     * @version 1.0
     * @description  RSA校验数字签名
     */
    public static boolean verify(byte[] data, byte[] sign, byte[] pubKey) throws Exception {
        // 实例化密钥工厂
        KeyFactory keyFactory = KeyFactory.getInstance(RSA_KEY_ALGORITHM);
        // 初始化公钥
        X509EncodedKeySpec x509KeySpec = new X509EncodedKeySpec(pubKey);
        // 产生公钥
        PublicKey publicKey = keyFactory.generatePublic(x509KeySpec);
        // 实例化Signature
        Signature signature = Signature.getInstance(SIGNATURE_ALGORITHM);
        // 初始化Signature
        signature.initVerify(publicKey);
        // 更新
        signature.update(data);
        // 验证
        return signature.verify(sign);
    }



    /**
     *
     * @return
     * @date    2023/10/5-11:22
     * @version 1.0
     * @description  生成 RSA 密钥对
     */
    public static KeyPair generateRsaKey(int keySize) {
        if(keySize==0){
            keySize = KEY_SIZE;
        }
        KeyPair keyPair;
        try {
            KeyPairGenerator keyPairGenerator = KeyPairGenerator.getInstance("RSA");
            keyPairGenerator.initialize(keySize);
            keyPair = keyPairGenerator.generateKeyPair();
        }
        catch (Exception ex) {
            throw new IllegalStateException(ex);
        }
        return keyPair;
    }

    /**
     *
     * @param key
     * @return
     * @date    2023/10/5-11:22
     * @version 1.0
     * @description  公钥转base64字符串
     */
    public static String publicKeyToBase64(RSAPublicKey key){
        return Base64Encoder.encode(key.getEncoded());
    }

    /**
     *
     * @param key
     * @return
     * @date    2023/10/5-11:23
     * @version 1.0
     * @description  私钥转base64字符串
     */
    public static String privateKeyToBase64(RSAPrivateKey key){
        return Base64Encoder.encode(key.getEncoded());
    }

    /**
     *
     * @param base64
     * @return
     * @date    2023/10/5-11:43
     * @version 1.0
     * @description  base64字符串转公钥
     */
    public static RSAPublicKey base64ToPublicKey(String base64)  {
        byte[] keyBytes = Base64Decoder.decode(base64.getBytes());
        X509EncodedKeySpec keySpec = new X509EncodedKeySpec(keyBytes);
        RSAPublicKey rsaPublicKey = null;
        try {
            KeyFactory keyFactory = KeyFactory.getInstance("RSA");
            rsaPublicKey = (RSAPublicKey)keyFactory.generatePublic(keySpec);
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException(e);
        } catch (InvalidKeySpecException e) {
            throw new RuntimeException(e);
        }

        return rsaPublicKey;
    }

    public static RSAPrivateKey base64ToPrivateKey(String base64)  {
        byte[] keyBytes = Base64Decoder.decode(base64.getBytes());
        PKCS8EncodedKeySpec keySpec = new PKCS8EncodedKeySpec(keyBytes);
        RSAPrivateKey rsaPrivateKey = null;
        try {
            KeyFactory keyFactory = KeyFactory.getInstance("RSA");
            rsaPrivateKey = (RSAPrivateKey)keyFactory.generatePrivate(keySpec);
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException(e);
        } catch (InvalidKeySpecException e) {
            throw new RuntimeException(e);
        }

        return rsaPrivateKey;
    }

    /**
     * 使用默认公钥加密数据（推荐使用）
     *
     * @param data 待加密的明文数据
     * @return 加密后的Base64字符串
     * @throws RuntimeException 加密失败时抛出
     */
    public static String encrypt(String data) {
        try {
            return encryptByPubKey(data, publicKeyBase64Default);
        } catch (Exception e) {
            throw new RuntimeException("加密数据失败: " + e.getMessage(), e);
        }
    }

    /**
     * 使用默认私钥解密数据（推荐使用）
     *
     * @param encryptedData 加密后的Base64字符串
     * @return 解密后的明文数据
     * @throws RuntimeException 解密失败时抛出
     */
    public static String decrypt(String encryptedData) {
        try {
            return decryptByPriKey(encryptedData, privateKeyBase64Default);
        } catch (Exception e) {
            throw new RuntimeException("解密数据失败: " + e.getMessage(), e);
        }
    }

    /**
     * 使用指定密钥对的公钥加密数据（高级用法）
     *
     * @param data 待加密数据
     * @param keyPair 密钥对
     * @return 加密后的字符串
     */
    public static String encryptWithKeyPair(String data, KeyPair keyPair) {
        try {
            RSAPublicKey publicKey = (RSAPublicKey) keyPair.getPublic();
            return encryptByPubKey(data, publicKeyToBase64(publicKey));
        } catch (Exception e) {
            throw new RuntimeException("使用指定密钥对加密失败: " + e.getMessage(), e);
        }
    }

    /**
     * 使用指定密钥对的私钥解密数据（高级用法）
     *
     * @param encryptedData 加密后的数据
     * @param keyPair 密钥对（必须与加密时使用的密钥对相同）
     * @return 解密后的字符串
     */
    public static String decryptWithKeyPair(String encryptedData, KeyPair keyPair) {
        try {
            RSAPrivateKey privateKey = (RSAPrivateKey) keyPair.getPrivate();
            return decryptByPriKey(encryptedData, privateKeyToBase64(privateKey));
        } catch (Exception e) {
            throw new RuntimeException("使用指定密钥对解密失败: " + e.getMessage(), e);
        }
    }

    /**
     * 检查字符串是否被RSA加密
     *
     * @param encryptedData 待检查的字符串
     * @return true-已加密, false-未加密或无效数据
     */
    public static boolean check(String encryptedData) {
        try {
            // 1. 检查是否为空
            if (encryptedData == null || encryptedData.trim().isEmpty()) {
                return false;
            }

            // 2. 检查是否是有效的Base64编码
            byte[] decoded = Base64Decoder.decode(encryptedData);
            if (decoded == null || decoded.length == 0) {
                return false;
            }

            // 3. 尝试用默认私钥解密，成功则说明是RSA加密数据
            decryptByPriKey(encryptedData, privateKeyBase64Default);
            return true;
        } catch (Exception e) {
            // 解密失败说明不是RSA加密数据或使用了不同的密钥对
            return false;
        }
    }

    public static void main(String[] args) throws Exception {
        // 测试数据
        String data = "wangao";

        String encrypted1 = RSAUtils.encrypt(data);
        System.out.println("加密前: " + data);
        System.out.println("加密后: " + encrypted1);
        String decrypted1 = RSAUtils.decrypt(encrypted1);
        System.out.println("解密后: " + decrypted1);
        System.out.println("验证成功: " + data.equals(decrypted1));

        String decrypted2 = RSAUtils.decrypt("d3BPspodbXm5FQBJAp4LUeJp+qBr4EIAYFJ9V0rANokhVbz80Bokex6bo4ei0gkiq5yaBbMiHGeRTYKYJBYCM4GSTvMijndd3T4lyoBzY+9sqZrLehdt7Yrd2s7tABB6ORIENmVuw8wi5fePgTdYDvfTOvQh6BN7XRvuPeYdN2c=");
        System.out.println("解密特定编码: " + decrypted2);

    }

}