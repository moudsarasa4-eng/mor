// Configuración de render. Vale igual en Windows, Mac o Linux.
import {Config} from '@remotion/cli/config';

Config.setVideoImageFormat('jpeg');
Config.setJpegQuality(92);
Config.setOverwriteOutput(true);
Config.setCodec('h264');
Config.setPixelFormat('yuv420p');
Config.setColorSpace('bt709'); // rango TV + bt709: lo que esperan Instagram y los celulares
Config.setCrf(18);
Config.setX264Preset('veryfast');
// Render 3D por CPU (funciona sin placa de video). En una PC con GPU podés probar 'angle'.
Config.setChromiumOpenGlRenderer('swangle');
// Si no hay internet para bajar Chrome, se puede apuntar a un Chrome ya instalado:
if (process.env.REMOTION_BROWSER) {
  Config.setBrowserExecutable(process.env.REMOTION_BROWSER);
}
