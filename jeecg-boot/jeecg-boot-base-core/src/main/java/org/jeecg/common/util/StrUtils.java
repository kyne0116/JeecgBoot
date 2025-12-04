package org.jeecg.common.util;

import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang.StringUtils;

import java.util.HashMap;
import java.util.Map;
import java.util.regex.Pattern;

@Slf4j
public class StrUtils {

    /**
     * 将map转换成url
     * @param map
     * @return
     */
    public static<T> String getUrlParamsByMap1(Map<String, T> map) {
        if (map == null) {
            return "";
        }
        StringBuffer sb = new StringBuffer();
        for (Map.Entry<String, T> entry : map.entrySet()) {
            sb.append(entry.getKey() + "=" + entry.getValue());
            sb.append("&");
        }
        String s = sb.toString();
        if (s.endsWith("&")) {
            s = org.apache.commons.lang.StringUtils.substringBeforeLast(s, "&");
        }
        return s;
    }

    public static<T> String getUrlParamsByMapEncodeUrl(Map<String, T> map) {
        if (map == null) {
            return "";
        }
        StringBuffer sb = new StringBuffer();
        for (Map.Entry<String, T> entry : map.entrySet()) {
            sb.append(entry.getKey() + "=" + Encodes.urlEncode(entry.getValue().toString()));
            sb.append("&");
        }
        String s = sb.toString();
        if (s.endsWith("&")) {
            s = org.apache.commons.lang.StringUtils.substringBeforeLast(s, "&");
        }
        return s;
    }

    /**
     * 将url参数转换成map
     * @param param aa=11&bb=22&cc=33
     * @return
     */
    public static Map<String, Object> getUrlParams(String param) {
        Map<String, Object> map = new HashMap<String, Object>(0);
        if (StringUtils.isBlank(param)) {
            return map;
        }
        String[] params = param.split("&");
        for (int i = 0; i < params.length; i++) {
            String[] p = params[i].split("=");
            if (p.length == 2) {
                map.put(p[0], p[1]);
            }
        }
        return map;
    }

    /**
     * 判断是否是合法ip地址
     * @param ipStr 要校验的字符串
     * @return
     * @data 2017年10月13日 @author zlxtk
     */
    public static boolean checkIP(String ipStr) {
        Pattern pattern = Pattern.compile("^((\\d|[1-9]\\d|1\\d\\d|2[0-4]\\d|25[0-5]"
                + "|[*])\\.){3}(\\d|[1-9]\\d|1\\d\\d|2[0-4]\\d|25[0-5]|[*])$");
        return pattern.matcher(ipStr).matches();
    }


}
