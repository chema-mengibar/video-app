import LocaleService from './locale-service';
import ConfigService from './config-service';
import ToolService from './tool-service';
import EditorService from './editor-service';
import VisualsService from './visuals-service';

const visualsService = new VisualsService();
const localeService = new LocaleService();
const configService = new ConfigService(localeService);
const toolService = new ToolService( visualsService );
const editorService = new EditorService();

export default {
    configService,
    localeService,
    toolService,
    editorService,
    visualsService
};
