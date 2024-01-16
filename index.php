<!DOCTYPE html>
<html data-bs-theme = "dark">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no" />
        <meta http-equiv="x-ua-compatible" content="ie=edge" />
        <title>Photos</title>

        <link rel="stylesheet" href="mdb/css/mdb.min.css" />
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" />
        <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700;900&display=swap" />
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-T3c6CoIi6uLrA9TneNEoa7RxnatzjcDSCmG1MXxSR1GAsXEV/Dwwykc2MPK8M2HN" crossorigin="anonymous">
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js" integrity="sha384-C6RzsynM9kWDrMNeT87bh95OGNyZPhcTNXj1NW7RuBCsyN/o0jlpcV8Qyq46cDfL" crossorigin="anonymous"></script>
        <script src="https://code.jquery.com/jquery-3.7.1.min.js" integrity="sha256-/JqT3SQfawRcv/BIHPThkBvs0OEvtFFmqPF/lYI/Cxo=" crossorigin="anonymous"></script>
        <script src='https://cdn.jsdelivr.net/npm/gasparesganga-jquery-loading-overlay@2.1.7/dist/loadingoverlay.min.js'></script>
        <!-- <script src="https://cdn.jsdelivr.net/npm/bs5-lightbox@1.8.3/dist/index.bundle.min.js"></script> -->
        <!-- <script type="module" src="lightbox.js"></script> -->
        <!-- <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@docsearch/css@3"> -->
        <link rel="stylesheet" href="photoswipe/photoswipe.css" />

        <script type="module">
            import PhotoSwipeLightbox from './photoswipe/photoswipe-lightbox.esm.min.js';
            import PhotoSwipeVideoPlugin from './photoswipe/photoswipe-video-plugin.esm.min.js';
            const lightbox = new PhotoSwipeLightbox ({
                gallery: '#gallery',
                children: 'a',
                pswpModule: () => import ('./photoswipe/photoswipe.esm.min.js')
            });

            const videoPlugin = new PhotoSwipeVideoPlugin (lightbox, {
            });

            lightbox.init ();
        </script>

        <script>
            function loadingComplete () {
                console.log ("done!");
                $.LoadingOverlay ('hide');
            };
        </script>

    </head>


    <!-- <body class="d-flex flex-column h-100"> -->
    <?php include 'photos.php'; ?>
    <body onload='loadingComplete()'>
        <script>
            $.LoadingOverlay ('show', {
                image: "",
                background: "rgba(255, 255, 255, 0.5)",
                fontawesome : "fas fa-cog fa-spin",
                fontawesomeAnimation: "pulse"
            });
        </script>

        <header class="mb-5 mb-lg-7">
            <?php
                navgn ();
                bg ();
            ?>
        </header>

        <main>
            <div class="container-fluid">
                <?php
                    // include 'photos.php';
                    $photoDir = 'data/day6done';
                    $maxHeight = 150;               //  max height of thumbnail
                    $folders = array ();
                    $files = array ();

                    getContents ($photoDir);


                    // foreach ($folders as $i) echo $i . " ";
                    // echo "<br />";
                    // foreach ($files as $i) echo $i . " ";
                    // echo "<br />";
                    echo "<h3 class='fw-bold text-center mt-3 mb-3'>" . $photoDir . "</h3>";

                    //  folders
                    echo "<section class='mb-5 mb-lg-10'>";
                    echo "  <div class='row gx-lx-5'>";
                        foreach ($folders as $i) {
                            card (basename($i), firstImg($i));
                        };
                    echo "  </div>";
                    echo "</section>";

                    //  files
                    echo "<section class='pswp-gallery pswp-gallery--single-column' id='gallery'>";
                    echo "  <div>";
                        foreach ($files as $i) {
                            thumbnail ($i);
                        };
                    echo "  </div>";
                    echo "</section>";
                ?>

            </div>
        </main>

        <?php footer (); ?>
        <script type="text/javascript" src="mdb/js/mdb.umd.min.js"></script>
    </body>
</html>
