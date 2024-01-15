<!DOCTYPE html>
<html data-bs-theme = "dark">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no" />
        <meta http-equiv="x-ua-compatible" content="ie=edge" />
        <link rel="stylesheet" href="mdb/css/mdb.min.css" />
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-T3c6CoIi6uLrA9TneNEoa7RxnatzjcDSCmG1MXxSR1GAsXEV/Dwwykc2MPK8M2HN" crossorigin="anonymous">
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js" integrity="sha384-C6RzsynM9kWDrMNeT87bh95OGNyZPhcTNXj1NW7RuBCsyN/o0jlpcV8Qyq46cDfL" crossorigin="anonymous"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" />
        <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700;900&display=swap" />
        <!-- <script src="https://cdn.jsdelivr.net/npm/bs5-lightbox@1.8.3/dist/index.bundle.min.js"></script> -->
        <!-- <script type="module" src="lightbox.js"></script> -->
        <!-- <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@docsearch/css@3"> -->
        <title>Photos</title>
    </head>


    <!-- <body class="d-flex flex-column h-100"> -->
    <?php include 'photos.php'; ?>
    <body>
        <!-- <div class="container-fluid" style="height: 500px;"> -->
            <header class="mb-5 mb-lg-7">
                <?php
                    navgn ();
                    bg ();
                ?>
            </header>
            <main>
            <?php
                // include 'photos.php';
                $photoDir = 'data';
                $folders = array ();
                $files = array ();

                echo "<h3 class='fw-bold text-center mt-3 mb-3'>" . $photoDir . "</h3>";

                getContents ($photoDir);

                foreach ($folders as $i) echo $i . " ";
                echo "<br />";
                foreach ($files as $i) echo $i . " ";
                echo "<br />";

                card ();
            ?>
            </main>

            <?php footer (); ?>
        <!-- </div> -->
        <script type="text/javascript" src="mdb/js/mdb.umd.min.js"></script>
    </body>
</html>
