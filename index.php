<!DOCTYPE html>
<html class='h-100' data-bs-theme = "dark">
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
        <link rel="stylesheet" href="photoswipe/photoswipe.css" />
        <script src="photos.js"></script>

        <style>
            .card-img {
                max-height: 200px;
                overflow: hidden;
            }
            .card-img img {
                width: 100%;
                height: auto;
            }
            .vid {
                display: inline-block;
                margin-bottom: -50;
                /* position: relative; */
                /* float: left; */
            }
            .overlay {
                position: absolute;
                top:0;
                left: 0;
            }
            .overlay2 {
                position: absolute;
                top:0;
                right: 0;
            }
        </style>

        <script type="module">
            import PhotoSwipeLightbox from './photoswipe/photoswipe-lightbox.esm.min.js';
            import PhotoSwipeVideoPlugin from './photoswipe/photoswipe-video-plugin.esm.min.js';
            const lightbox = new PhotoSwipeLightbox ({
                gallery: '#gallery',
                children: 'a',
                // showHideAnimationType: 'fade',
                pswpModule: () => import ('./photoswipe/photoswipe.esm.min.js')
            });

            const videoPlugin = new PhotoSwipeVideoPlugin (lightbox, {
            });

            lightbox.init ();
        </script>
    </head>


    <?php
        include 'photos.php';
        $photoDir = '';

        if (isset ($_GET['d'])) $photoDir = $_GET['d'];
    ?>

    <body class='d-flex flex-column h-100' onload='loadingComplete()'>
        <script>
            $.LoadingOverlay ('show', {
                image: "",
                background: "rgba(50, 50, 50, 0.8)",
                fontawesome: "fas fa-cog fa-spin",
                fontawesomeColor: "#DDDDDD"
                // fontawesomeAnimation: "fadein"
            });
        </script>

        <?php //pHeader (); ?>
        <main class='mb-3'>
            <div class="container-fluid">
                <?php
                    $folders = array ();
                    $files = array ();
                    getContents ($photoDir);

                    echo "<h3 class='fw-bold text-center my-3'>" . ($photoDir == '' ? "Home" : basename($photoDir)) . "</h3>";
                    breadcrumbsT ();

                    //  folders
                    echo "<section class='mb-5 mb-lg-10'>";
                    echo "  <div class='row gx-lx-5'>";
                        foreach ($folders as $i) {
                            card ($i, firstImg($i));
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
        <?php pFooter (); ?>

        <script type="text/javascript" src="mdb/js/mdb.umd.min.js"></script>
    </body>
</html>
