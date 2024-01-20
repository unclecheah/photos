<html>
    <head>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js" integrity="sha384-MrcW6ZMFYlzcLA8Nl+NtUVF0sA7MsXsP1UyJoMp4YLEuNSfAP+JcXn/tWtIaxVXM" crossorigin="anonymous"></script>
        <!-- <script src="https://cdn.jsdelivr.net/npm/bs5-lightbox@1.8.3/dist/index.bundle.min.js"></script> -->
        <link rel="stylesheet" href="photoswipe/photoswipe.css" />

        <script type="module">
            import PhotoSwipeLightbox from './photoswipe/photoswipe-lightbox.esm.min.js';
            import PhotoSwipeVideoPlugin from './photoswipe/photoswipe-video-plugin.esm.min.js';
            const lightbox = new PhotoSwipeLightbox ({
                gallery: '#gallery-img',
                children: 'a',
                pswpModule: () => import ('./photoswipe/photoswipe.esm.min.js')
            });

            const videoPlugin = new PhotoSwipeVideoPlugin (lightbox, {
            });

            lightbox.init ();
        </script>
    </head>

    <body>
        <div class="pswp-gallery pswp-gallery--single-column" id="gallery-img">
          <a href="data/bali/Bali-20231223-100932-ATV.jpg"
            data-pswp-width="800"
            data-pswp-height="600"
            target="_blank">
            <img src="fs2.webp" alt="" />
          </a>
          <!-- cropped thumbnail: -->
          <a href="data/bali/Bali-20231223-090552-ATV.jpg"
            data-pswp-width="1875"
            data-pswp-height="2500"
            data-cropped="true"
            target="_blank">
            <img src="fs2.webp" alt="" />
          </a>
          <a href="data/bali/Bali-20231223-102038-ATV.mp4"
              data-pswp-type="video"
              data-pswp-width="1875"
              data-pswp-height="2500"
              target="_blank">
              <img src="fs2.webp" alt="" />
          </a>
       </div>
       <div class="pswp-gallery pswp-gallery--single-column" id="gallery-vid">
      </div>
          <!-- data-pswp-src with custom URL in href -->
          <!-- <a href="https://unsplash.com"
            data-pswp-src="https://cdn.photoswipe.com/photoswipe-demo-images/photos/3/img-2500.jpg"
            data-pswp-width="2500"
            data-pswp-height="1666"
            target="_blank">
            <img src="https://cdn.photoswipe.com/photoswipe-demo-images/photos/3/img-200.jpg" alt="" />
          </a> -->
          <!-- Without thumbnail: -->
          <!-- <a href="http://example.com"
            data-pswp-src="data/bali/Bali-20231223-070822.jpg"
            data-pswp-width="2500"
            data-pswp-height="1668"
            target="_blank">
            No thumbnail
          </a> -->
          <!-- wrapped with any element: -->
          <!-- <div>
            <a href="https://cdn.photoswipe.com/photoswipe-demo-images/photos/6/img-2500.jpg"
              data-pswp-width="2500"
              data-pswp-height="1667"
              target="_blank">
              <img src="https://cdn.photoswipe.com/photoswipe-demo-images/photos/6/img-200.jpg" alt="" />
            </a>
          </div> -->
        </div>
    </body>
</html>
