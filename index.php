<html>
    <body>
        <?php
        // header('Content-Type: image/jpeg');

        // Set the directory path to your folder of images
        $imageDirectory = 'data/';

        // Set the desired maximum width and height for the scaled images
        $maxWidth = 200;
        $maxHeight = 150;

        // Get a list of image files in the directory
        $imageFiles = glob($imageDirectory . '*.{jpg,jpeg,png,gif}', GLOB_BRACE);

        // Loop through each image file in the directory
        foreach ($imageFiles as $imagePath) {
            // Load the original image
            $originalImage = imagecreatefromjpeg($imagePath); // Adjust for different file types if needed

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

            ob_start ();
            // Set content type to JPEG and enable progressive rendering
            // header('Content-Type: image/jpeg');
            imageinterlace($resizedImage, true); // Enable progressive rendering

            // Output the resized image to the browser with the specified quality
            imagejpeg($resizedImage, null, 85); // Adjust quality as needed
            $raw = ob_get_clean ();
            echo "<img src='data:image/jpeg;base64," . base64_encode ($raw) . "' />";
            // ob_end_flush ();

            // Clean up resources for the current image
            imagedestroy($originalImage);
            imagedestroy($resizedImage);
        }
        ?>

    </body>
</html>
