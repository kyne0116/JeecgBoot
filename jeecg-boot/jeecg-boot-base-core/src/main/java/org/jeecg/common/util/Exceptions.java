package org.jeecg.common.util;

import lombok.extern.slf4j.Slf4j;

import java.io.ByteArrayOutputStream;
import java.io.PrintWriter;
import java.io.StringWriter;

@Slf4j
public class Exceptions {

    /**
     * 将CheckedException转换为UncheckedException.
     */
    public static RuntimeException unchecked(Exception e) {
        if (e instanceof RuntimeException) {
            return (RuntimeException) e;
        } else {
            return new RuntimeException(e);
        }
    }

    /**
     * 将ErrorStack转化为String.
     */
    public static String getStackTraceAsString(Exception e) {
        StringWriter stringWriter = new StringWriter();
        e.printStackTrace(new PrintWriter(stringWriter));
        return stringWriter.toString();
    }

    /**
     * 判断异常是否由某些底层的异常引起.
     */
    public static boolean isCausedBy(Exception ex, @SuppressWarnings("unchecked") Class<? extends Exception>... causeExceptionClasses) {
        Throwable cause = ex;
        while (cause != null) {
            for (Class<? extends Exception> causeClass : causeExceptionClasses) {
                if (causeClass.isInstance(cause)) {
                    return true;
                }
            }
            cause = cause.getCause();
        }
        return false;
    }

    public static void printException(Exception e){
        ByteArrayOutputStream buf = new ByteArrayOutputStream();
        e.printStackTrace(new PrintWriter(buf, true));
        String expMsg = buf.toString();
        if(!expMsg.contains("UnknownSessionException") && !expMsg.contains("invalid_request, Missing grant_type")) {
            log.error(expMsg);
        }
    }

}
