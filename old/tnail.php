<html>
    <body>
        <?php
        $imageDirectory = 'data/bali/';

        // Set the desired maximum width and height for the scaled images
        $maxWidth = 200;
        $maxHeight = 150;
        $fsHeight = 425;            //  film strip corner overlay
        $mime = "";                 //  chk if file is video

        // Get a list of image files in the directory
        // $imageFiles = glob($imageDirectory . '*.{jpg,jpeg,png,gif}', GLOB_BRACE);
        $imageFiles = glob($imageDirectory . '*', GLOB_BRACE);


        function processImage ($file) {
            global $maxWidth, $maxHeight;

            $originalImage = imagecreatefromjpeg($file); // Adjust for different file types if needed

            // Get the original image dimensions
            $originalWidth = imagesx($originalImage);
            $originalHeight = imagesy($originalImage);

            // Calculate the new dimensions while maintaining aspect ratio
            if ($originalWidth > $maxWidth || $originalHeight > $maxHeight) {
                $aspectRatio = $originalWidth / $originalHeight;

                if ($maxWidth / $maxHeight > $aspectRatio) {
                    $newWidth = $maxHeight * $aspectRatio;
                    $newHeight = $maxHeight;
                } else {
                    $newWidth = $maxWidth;
                    $newHeight = $maxWidth / $aspectRatio;
                }
            } else {
                $newWidth = $originalWidth;
                $newHeight = $originalHeight;
            }

            // Create a new image with the calculated dimensions
            $resizedImage = imagecreatetruecolor($newWidth, $newHeight);

            // Perform the image copy and resizing
            imagecopyresampled($resizedImage, $originalImage, 0, 0, 0, 0, $newWidth, $newHeight, $originalWidth, $originalHeight);


            /////   to save image   /////
            // $out = imagecreatetruecolor ($newWidth, $newHeight);
            // imagejpeg ($resizedImage, $imagePath . "-1.jpg", 100);
            /////////////////////////////


            ob_start ();
            // Set content type to JPEG and enable progressive rendering
            // header('Content-Type: image/jpeg');
            imageinterlace($resizedImage, true); // Enable progressive rendering

            // Output the resized image to the browser with the specified quality
            imagejpeg($resizedImage, null, 85); // Adjust quality as needed
            $raw = ob_get_clean ();
            echo "<img src='data:image/jpeg;base64," . base64_encode ($raw) . "' />\n";
            // ob_end_flush ();

            // Clean up resources for the current image
            imagedestroy($originalImage);
            imagedestroy($resizedImage);

        }

        function processVideo () {
            echo "<img src='fs2.webp' />\n";
        }

        // Loop through each image file in the directory
        foreach ($imageFiles as $imagePath) {
            $mime = mime_content_type ($imagePath);
            if (strstr ($mime, "video/")) {
                processVideo ($imagePath);
            } else {
                processImage ($imagePath);
            }
        }
        ?>

    </body>
</html>
