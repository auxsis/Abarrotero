odoo.define('report_qz_printer.qweb_action_manager', function(require) {
    'use strict';

    let ActionManager = require('web.ActionManager');
    let session = require('web.session');
    let rpc = require('web.rpc');

    /// Authentication setup ///
    qz.security.setCertificatePromise(function(resolve, reject) {
        //Preferred method - from server
//        fetch("assets/signing/digital-certificate.txt", {cache: 'no-store', headers: {'Content-Type': 'text/plain'}})
//          .then(function(data) { data.ok ? resolve(data.text()) : reject(data.text()); });

        //Alternate method 1 - anonymous
//        resolve();  // remove this line in live environment

        //Alternate method 2 - direct

        //Aquí va el contenido de cert.pem
        resolve("-----BEGIN CERTIFICATE-----\n" +
            "MIIERzCCAy+gAwIBAgIUXyQEz7wh1kVr2FZxgw+GljQ0O5QwDQYJKoZIhvcNAQEL\n" +
            "BQAwgbExCzAJBgNVBAYTAk1YMQswCQYDVQQIDAJERjEPMA0GA1UEBwwGTWV4aWNv\n" +
            "MRUwEwYDVQQKDAxPZG9vIGV4cGVydHMxFTATBgNVBAsMDE9kb28gRXhwZXJ0czEh\n" +
            "MB8GA1UEAwwYb2Rvby5ncnVwb2FiYXJyb3Rlcm8uY29tMTMwMQYJKoZIhvcNAQkB\n" +
            "FiRnYWJyaWVsLnJvZHJpZ3VlekBvZG9vZXhwZXJ0cy5jb20ubXgwIBcNMjAxMDEx\n" +
            "MTUxMTM4WhgPMjA1MjA0MDUxNTExMzhaMIGxMQswCQYDVQQGEwJNWDELMAkGA1UE\n" +
            "CAwCREYxDzANBgNVBAcMBk1leGljbzEVMBMGA1UECgwMT2RvbyBleHBlcnRzMRUw\n" +
            "EwYDVQQLDAxPZG9vIEV4cGVydHMxITAfBgNVBAMMGG9kb28uZ3J1cG9hYmFycm90\n" +
            "ZXJvLmNvbTEzMDEGCSqGSIb3DQEJARYkZ2FicmllbC5yb2RyaWd1ZXpAb2Rvb2V4\n" +
            "cGVydHMuY29tLm14MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2WXS\n" +
            "A7tFH32xV04m5Qudxo6l6RxEjmHbuBudb2t7gFx9lC7IZh7z8EesGOsm4GL6DPpr\n" +
            "8QfANxwOLPCuNvRMOL/njMWCWF22wtZwb0y7f2Eu5mxhgQHCbIHbMp/BB9YyRNw8\n" +
            "Ypfh/msNYCUcxt7ONPaIfnpm6IQhpoTZUUYZgtDjTNP4Bux3Ji7IxBJWLOic4AQJ\n" +
            "EFCiVwu9gEMdRLafa9UW73XwnWUmnJ0c85fNsoTVAlqG3B9Y75oRlNHEon9ETTvM\n" +
            "c0UjRJE3PKIfDsgjUBNVOdE2v0ByrtAnYOdWRhE7KB/z8ughDBMiijknTpz4nk4R\n" +
            "eWNSvx8eE38arLC8hwIDAQABo1MwUTAdBgNVHQ4EFgQUuo7J46wFp8Bzgpkz3Wxz\n" +
            "jvTNxeMwHwYDVR0jBBgwFoAUuo7J46wFp8Bzgpkz3WxzjvTNxeMwDwYDVR0TAQH/\n" +
            "BAUwAwEB/zANBgkqhkiG9w0BAQsFAAOCAQEAdl3G3f+LNSj/MWPDoyeABURoY2A2\n" +
            "5kby9CNAoD7FQlMuRQQow1bvQq+MthAb55ww1mI8baxd68x/Ji0AUWdf2SOYorXt\n" +
            "xaLceZcjsR2qq3CTpaf/BuOMxlCZ/KHn7R8XrQKiQJw9Wg2AFJ2MAaI2eKhsLwqP\n" +
            "AGZizo/FBWYazHYqxD5/Bh08IpcCPvHnNvv8GtlFquJDOP+JK9pq3nTgW+opkJM/\n" +
            "stJW2FHZf+ImTvbDlyUrneU5u2ZNH6ZnycEF+VGYzoMIElBoyRdYbvk2WZnE4MdD\n" +
            "Ud+oS1kQoAyHCQAWxeRkLjBatlidoPu3sqdbZZe/5wfMlYCAAjmGZq7/8g==\n" +
            "-----END CERTIFICATE-----");
    });

    //Aquí va el contenido de key.pem
    let privateKey = "-----BEGIN PRIVATE KEY-----\n" +
        "MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDZZdIDu0UffbFX\n" +
        "TiblC53GjqXpHESOYdu4G51va3uAXH2ULshmHvPwR6wY6ybgYvoM+mvxB8A3HA4s\n" +
        "8K429Ew4v+eMxYJYXbbC1nBvTLt/YS7mbGGBAcJsgdsyn8EH1jJE3Dxil+H+aw1g\n" +
        "JRzG3s409oh+embohCGmhNlRRhmC0ONM0/gG7HcmLsjEElYs6JzgBAkQUKJXC72A\n" +
        "Qx1Etp9r1RbvdfCdZSacnRzzl82yhNUCWobcH1jvmhGU0cSif0RNO8xzRSNEkTc8\n" +
        "oh8OyCNQE1U50Ta/QHKu0Cdg51ZGETsoH/Py6CEMEyKKOSdOnPieThF5Y1K/Hx4T\n" +
        "fxqssLyHAgMBAAECggEAHFNK8NeGoxrCb4isQq2nygYuEdhwCkkv0qYudiT/+3KR\n" +
        "niwWSlAAIq+D+d8xuozK3cQHKmmDHusV4b8eQ+TCxaYjalEVsaPMO0irb6UEzQ0B\n" +
        "il5WufNbvL2SrN7pzLaY6CX17Daz6G1UWdGcFUFUhswUbr5OCD+nDsZCdnd2vXdy\n" +
        "lTVC2Ea4b9kBypa14A+IJbEuvG1kUIH13bl+7nkanYEIsaJAopAe3DJ8DHrDVE+A\n" +
        "TleLeCe6292XLS1iDAXpZpIWEM6VSPIq/r3lxcm6qRG4O6ZQo7/5kjAfSAzcGl8N\n" +
        "KV7dwClAbt/cgtH8JuezfiGec2Eyq8yp7RgxLqV6yQKBgQDzK14cOCnXM50b6EL9\n" +
        "tdwY+LGVr0mN7bVS5PyVIF8qt+dBX4aC+bjuIJuZUpgj2iVLcjSJeERHFk0LhNfz\n" +
        "UrA60P1cZr2SdrRNllDbH3vw+mQfd3ltxNaVbCyRLTaerpRArPzct/DuEW6ogWZM\n" +
        "n2fOf7PQV1Ui7yK9D88lLO2Y7QKBgQDk3lbyk5AG6YByjznKfHaMcPNmpjAZqTeG\n" +
        "lmC+pY4EWWZRetxiAzoDh7AUtCGyU85qTG2HKFbbasfhfmAxYsHkoBXisi4aL+Je\n" +
        "7zt0VQFK/ACoJvCOELrzaSSEW8ynbPEa935gYYUbaTNCpAuyg65VBqzTGyun2lGm\n" +
        "i6S89iJAwwKBgQC/F/+XEZPf6FG40qeCld3nSdjUlrGo9XsfL5BG6O+gtHDpcNZW\n" +
        "K0Tm7X0Z2kxxMEdKqO8ccQTHEIFvYfAK6ZpQPlg8uwiTBvHeXxgfevh9gWgZSlyE\n" +
        "pME1H5NOa0eXH/6lbMwx7+NIUy6xAS+RW1vKbZSzT046a87S4I+a2VnGaQKBgD7A\n" +
        "W5SdMwNCKI7AiHblU1fEbGg7rrqKdAf52ULMf7jfjjdO+XgCLHjlTjkO/qI3akQo\n" +
        "+mrxe4cjqvQ/wz4nNsRpxDZo5k0Vzfp7m5CU8grON5vjOVeqbKfqrzF/Pgi1zRG4\n" +
        "xDTG6EkQuhZOhkqG4li7wM0NCRY3vOVuKlgJIHEjAoGBAKZIv02VZbekjOvHlUZg\n" +
        "t4fFfJv2bJWML8NueXfIOze7WK6yr4CIcLPuD1iVjOkSvrzl53YTz2MFCurnWXt7\n" +
        "dHbJpku0eNhSfTsWjolHgEDe0e6c+8ajYc95VjFnlcyYI9xvaYMJDaHp4YNfYgYV\n" +
        "Y9iEWu+MnPgoO4BBt3dmMS6g\n" +
        "-----END PRIVATE KEY-----";

    qz.security.setSignatureAlgorithm("SHA512"); // Since 2.1
    qz.security.setSignaturePromise(function(toSign) {
        return function(resolve, reject) {
            try {
                let pk = KEYUTIL.getKey(privateKey);
                let sig = new KJUR.crypto.Signature({"alg": "SHA512withRSA"});  // Use "SHA1withRSA" for QZ Tray 2.0 and older
                sig.init(pk);
                sig.updateString(toSign);
                let hex = sig.sign();
                console.log("DEBUG: \n\n" + stob64(hextorstr(hex)));
                resolve(stob64(hextorstr(hex)));
            } catch (err) {
                console.error(err);
                reject(err);
            }
        };
    });

    /// Connection ///
    function startConnection(company_id, data2print) {
        if (!qz.websocket.isActive()) {
            qz.websocket.connect().then(function() {
                console.log('Connection success');
                findVersion(company_id, data2print);
            }).catch(function(err) {
                alert(err || 'Connection failed');
            });
        } else {
            getPrinterFromOdoo(company_id, data2print);
        }
    }

    /// Page load ///
    function findVersion(company_id, data2print) {
        qz.api.getVersion().then(function(data) {
            let qz_version = qz.version
            if (data !== qz_version)
                alert('QZ Tray Version must be equal to ' + qz_version);
            else
                getPrinterFromOdoo(company_id, data2print);
        }).catch(function(err) {
            alert(err || 'Connection failed');
        });
    }

    /// Detection ///
    // Based on findPrinter from sample.html file
    function getPrinterFromOdoo(company_id, data2print) {
        rpc.query({
                model: 'res.company',
                method: 'read',
                args: [[company_id], []],
            }, undefined
        ).done(function(company) {
            let pos_printer = company[0].pos_printer;
            qz.printers.find(pos_printer).then(function(printer) {
                console.log("Found: " + printer);
                setPrinter(printer);
                printReport(data2print);
            }).catch(function(err) {
                console.log("Found Printer Error:", err);
            });
        });
    }

    /// QZ Config ///
    // From sample.html check function named updateConfig
    let cfg = null;
    function getUpdatedConfig() {
        if (cfg == null) {
            cfg = qz.configs.create(null);
        }

        cfg.reconfigure({
            copies: 1,
            margins: {top: 0, left: 0.75},

        });
        return cfg
    }

    function setPrinter(printer) {
        let cf = getUpdatedConfig();
        cf.setPrinter(printer);
    }

    /// Pixel Printers ///
    function printReport(data2print) {
        let config = getUpdatedConfig();
        // From sample.html check function named getUpdatedOptions
        // let opts = getUpdatedOptions(true);
        let opts = {
            pageWidth: "", // $("#pPxlWidth").val(),
            pageHeight: "", // $("#pPxlHeight").val()
        };

        let printData = [
            {
                type: 'pixel',
                format: 'pdf',
                flavor: 'base64',
                data: data2print,
                options: opts
            }
        ];

        qz.print(config, printData).catch(function(err) {
            alert(err || 'Connection failed');
        });
    }

    ActionManager.include({
        _executeReportAction: function (action, options) {
            let use_qz = false;
            let company_id = session.company_id;
            rpc.query({
                    model: 'res.company',
                    method: 'read',
                    args: [[company_id], []],
                }, {async: false}
            ).done(function(company) {
                use_qz = company[0].use_qz;
            });

            if (
                use_qz &&
                (
                    [
                        'sale.order', 'purchase.order',
                    ].indexOf(action.model) > -1
                )
            ) {
                let url = this._makeReportUrls(action).pdf;


                pdfToBase64(url).then(function (data){
                    startConnection(company_id, data);
                }).catch(function (err){
                    alert(err || 'Connection failed');
                })

                return $.Deferred().reject();
            }

            return this._super(action, options);
        },
    });
});
