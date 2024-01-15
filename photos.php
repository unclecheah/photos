<?php
    $folders;
    $files;


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


    function footer () {
        echo <<<EOD
            <footer class="footer mt-auto py-3 bg-body-tertiary">
                <div class="container">
                    <span class="text-body-secondary">Place sticky footer content here.</span>
                </div>
            </footer>
        EOD;
    };


    function card () {
        $output = " <div class='card'>"
                . "     <div class='bg-image'>"
                . "         <img src='fs2.webp' class='img-fluid' />"
                . "         <a href='#!'>"
                . "         </a>"
                . "     </div>"
                . "     <div class='card-body'>"
                . "         <h5 class='card-title'>Card title</h5>"
                . "         <p class='card-text'>Some quick example text to build on the card title and make up the bulk of the card's content.</p>"
                . "     </div>"
                . " </div>";

        echo $output;
    };


    function getContents ($dir) {
        global $folders;
        global $files;

        $items = scandir($dir, 0);
        for ($i = 0; $i < count($items); $i++) {
            if ($items[$i] == "." || $items[$i] == "..") continue;
            if (is_dir ($dir . "/" . $items[$i])) array_push ($folders, $items[$i]);
            else array_push ($files, $items[$i]);
        }
    };
?>
