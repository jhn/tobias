<?php
// be aware of file / directory permissions on your server
move_uploaded_file($_FILES['webcam']['tmp_name'], 'uploads/webcam.jpg');
?>
