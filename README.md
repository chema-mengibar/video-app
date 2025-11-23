# video-app



````
src/
  app/                        # tu paquete principal (actual `app`)
    __init__.py
    main.py                   # entrypoint minimal -> call create_app
    factory.py                # create_app(config) <- wiring de dependencias
    config.py
    ui/                       # solo UI: widgets, windows, themes
      main_window.py
      widgets/
      components/
    services/                 # lógica desacoplada
      video_service.py
      draw_service.py
    adapters/                 # adaptadores a tecnologías concretas
      opencv_video_adapter.py  # implementa VideoProcessorInterface
      storage_filesystem.py
    features/                 # features independientes (cada carpeta)
      draw/
        manager.py
        tests/
      timeline/
    tests/
      unit/
      integration/
  pyproject.toml
  tox.ini / .github/workflows/ci.yml

```