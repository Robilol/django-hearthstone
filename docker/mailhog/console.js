'use strict';

// mailhog

module.exports = {

    questions: [
        {
            message: "Smtp server port",
            name: "smtp_server_port",
            default: "1025",
            validator: (value)=>{
                if(Skyflow.isPortReachable(value)){
                    return 'This port is not available.'
                }
                Skyflow.addDockerPort(value);
                return true
            }
        },
        {
            message: "Web server port",
            name: "web_server_port",
            default: "8025",
            validator: (value)=>{
                if(Skyflow.isPortReachable(value)){
                    return 'This port is not available.'
                }
                Skyflow.addDockerPort(value);
                return true
            }
        },
    ],

};
