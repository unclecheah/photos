<?php
    function navgn () {
        echo <<<EOD
        <nav style="z-index: 1; min-height: 58.9px;" class="navbar navbar-expand-lg navbar-dark bg-dark">
            <div class="container-fluid">
                <button data-mdb-collapse-init class="navbar-toggler" type="button" data-mdb-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
                    <i class="fas fa-bars"></i>
                </button>

                <div class="collapse navbar-collapse" id="navbarSupportedContent">
                    <a class="navbar-brand mt-2 mt-lg-0" href="#">
                        <i class="fas fa-gem text-secondary"></i>
                        <!-- <img src="https://mdbcdn.b-cdn.net/img/logo/mdb-transaprent-noshadows.webp" height="15" alt="MDB Logo" loading="lazy" /> -->
                    </a>
                    <ul class="navbar-nav me-auto mb-2 mb-lg-0">
                        <li class="nav-item"><a class="nav-link text-secondary fw-bold" href="#">About</a></li>
                        <li class="nav-item"><a class="nav-link text-secondary fw-bold" href="#">Projects</a></li>
                        <li class="nav-item"><a class="nav-link text-secondary fw-bold" href="#">Contact</a></li>
                    </ul>
                </div>

                <div class="d-flex align-items-center">
                    <a class="text-secondary me-3" href="https://www.youtube.com/c/Mdbootstrap/videos" rel="nofollow" target="_blank">
                        <i class="fab fa-youtube"></i>
                    </a>
                    <a class="text-secondary me-3" href="https://twitter.com/ascensus_mdb" rel="nofollow" target="_blank">
                        <i class="fab fa-twitter"></i>
                    </a>
                    <a class="text-secondary me-3" href="https://github.com/mdbootstrap/mdb-ui-kit" rel="nofollow" target="_blank">
                        <i class="fab fa-github"></i>
                    </a>
                </div>
            </div>
        </nav>
        EOD;
    };


    function bg () {
        echo <<<EOD
        <div class="bg-image vh-100" style="margin-top: -58.9px; background-image: url('mdb/img/018.jpg');">
            <div class="mask" style="background-color: hsla(0, 0%, 0%, 0.6)">
                <div class="container d-flex justify-content-center align-items-center h-100">
                    <div class="text-white text-center">
                        <h1 class="mb-3">Whoah, what a view!</h1>
                        <h5 class="mb-4">Learning web design is such an amazing thing</h5>
                        <a class="btn btn-secondary btn-lg m-2" href="#" role="button">Learn with me<i class="fas fa-graduation-cap ms-2"></i></a>
                    </div>
                </div>
            </div>
        </div>
        EOD;
    }


    function pHeader () {
        echo "<header class='mb-3'>";
        navgn ();
        bg ();
        echo "</header>";
    };


    function breadcrumbsT () {
        echo <<<EOD
        <div class="container">
        <nav style="--bs-breadcrumb-divider: '>';" aria-label="breadcrumb">
        <ol class="breadcrumb breadcrumb-custom overflow-hidden text-center bg-body-tertiary border rounded-3">
        <li class="breadcrumb-item">
        <a class="link-body-emphasis fw-semibold text-decoration-none" href="/">
        <svg class="bi" width="16" height="16"><use xlink:href="#house-door-fill"></use></svg>
        Home
        </a>
        </li>
        </ol>
        </nav>
        </div>
        EOD;
    };


    function pFooter () {
        echo <<<EOD
            <footer class="footer mt-auto py-3 bg-body-tertiary">
                <div class="container">
                    <span class="text-body-secondary">&#169; unclecheah</span>
                </div>
            </footer>
        EOD;
    };


    function firstImg ($dir) {
        global $photoRoot;
        $files = scandir ($photoRoot . "/" . $dir);
        return $photoRoot . "/" . $dir . "/" . $files[2];
    };


    function card ($fpath, $img) {
        global $maxHeight;

        $cardTitle = basename ($fpath);
        $output = " <div class='col-lg-2 col-md-4 col-sm-6 mb-4'>"
                . "     <div class='card h-100'>"
                . "         <div class='bg-image' style='height: ${maxHeight}'>"
                . "             <a href='?d=${fpath}'>"
                . "                 <div class='card-img'>"
                . "                     <img class='img-fluid' src='${img}' />"
                . "                 </div>"
                . "             </a>"
                . "         </div>"
                . "         <div class='card-body'>"
                . "             <h5 class='card-title'>${cardTitle}</h5>"
                // . "             <p class='card-text'>Some quick example text to build on the card title and make up the bulk of the card's content.</p>"
                . "         </div>"
                . "     </div>"
                . " </div>";

        echo $output;
    };


    function processVideo ($file) {
        global $photoRoot;
        global $maxHeight;
        global $imgFilmStrip;

        echo "<a style='display:inline-block;' href='${photoRoot}/${file}' data-pswp-type='video' target='_blank'>"
            . "     <img class='mb-1 me-1' src='${imgFilmStrip}' height='${maxHeight}' alt='' />"
            . " </a>";
    };


    function processImage ($file) {
        global $photoRoot;
        global $maxHeight;

        $originalImage = imagecreatefromjpeg($photoRoot . "/" . $file);
        $originalWidth = imagesx($originalImage);
        $originalHeight = imagesy($originalImage);
        $scaleFactor = $maxHeight / $originalHeight;
        $newHeight = $maxHeight;
        $newWidth = floor ($scaleFactor * $originalWidth);

        $resizedImage = imagecreatetruecolor($newWidth, $newHeight);
        imagecopyresampled($resizedImage, $originalImage, 0, 0, 0, 0, $newWidth, $newHeight, $originalWidth, $originalHeight);

        /////   to save image   /////
        // $out = imagecreatetruecolor ($newWidth, $newHeight);
        // imagejpeg ($resizedImage, $imagePath . "-1.jpg", 100);
        /////////////////////////////

        ob_start ();
        imageinterlace($resizedImage, true); // Enable progressive rendering
        imagejpeg($resizedImage, null, 85); // Adjust quality as needed
        $raw = ob_get_clean ();
        // ob_end_flush ();
        echo "<a style='display:inline-block;' href='${photoRoot}/${file}' data-pswp-width='${originalWidth}' data-pswp-height='${originalHeight}' target='_blank'>"
            . "     <img class='mb-1 me-1' src='data:image/jpeg;base64," . base64_encode ($raw) . "' alt='' />"
            . " </a>";
        imagedestroy($originalImage);
        imagedestroy($resizedImage);
    };


    function thumbnail ($infile) {
        global $photoRoot;

        $mime = mime_content_type ($photoRoot . "/" . $infile);
        if (strstr ($mime, "video/") || strstr ($mime, "octet-stream")) {
            processVideo ($infile);
        } else {
            processImage ($infile);
        }
    };


    function getContents ($dir) {
        global $photoRoot;
        global $folders;
        global $files;

        $workingDir = $dir == "" ? $photoRoot : $photoRoot . "/" . $dir;

        $items = scandir($workingDir, 0);
        for ($i = 0; $i < count($items); $i++) {
            if ($items[$i] == "." || $items[$i] == "..") continue;

            if (is_dir ($workingDir . "/" . $items[$i])) {
                array_push ($folders, $dir == '' ? $items[$i] : $dir . "/" . $items[$i]);
            } else {
                array_push ($files, $dir == '' ? $items[$i] : $dir . "/" . $items[$i]);
            }
        }
    };
?>
