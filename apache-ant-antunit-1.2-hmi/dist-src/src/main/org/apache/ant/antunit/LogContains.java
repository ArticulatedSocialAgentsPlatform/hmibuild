/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 * 
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 *
 */

package org.apache.ant.antunit;

import org.apache.tools.ant.BuildException;
import org.apache.tools.ant.Project;
import org.apache.tools.ant.ProjectComponent;
import org.apache.tools.ant.taskdefs.Echo;
import org.apache.tools.ant.taskdefs.condition.Condition;

/**
 * A condition that tests the log output of the current project for a
 * given string.
 *
 * <p>Works in conjunction with {@link LogCapturer LogCapturer} and
 * needs the context provided by AntUnit.</p>
 */
public class LogContains extends ProjectComponent implements Condition {

    private String text;
    private int logLevel = Project.MSG_INFO;

    /**
     * Test the log shall contain.
     */
    public void setText(String t) {
        text = t;
    }

    /**
     * minimal log priority to consult.
     */
    public void setLevel(Echo.EchoLevel echoLevel) {
        logLevel = echoLevel.getLevel();
    }

    public boolean eval() {
        if (text == null) {
            throw new BuildException("the text attribute is required");
        }
        Object o = getProject().getReference(LogCapturer.REFERENCE_ID);
        if (o instanceof LogCapturer) {
            LogCapturer c = (LogCapturer) o;
            String log;
            switch (logLevel) {
            case Project.MSG_ERR:
                log = c.getErrLog();
                break;
            case Project.MSG_WARN:
                log = c.getWarnLog();
                break;
            case Project.MSG_INFO:
                log = c.getInfoLog();
                break;
            case Project.MSG_VERBOSE:
                log = c.getVerboseLog();
                break;
            case Project.MSG_DEBUG:
                log = c.getDebugLog();
                break;
                
            default:
                throw new BuildException("Unknown logLevel: " + logLevel);
            }
            return log.indexOf(text) > -1;
        }
        return false;
    }
}
