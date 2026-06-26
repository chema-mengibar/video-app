import { reactive } from 'vue'

export const defaultLang = 'es'
export const keyLang = 'l'


export default class ConfigService {

    constructor(localeService) {

        this._localeService = localeService

        var params = new URLSearchParams(window.location.search);
        const langQueryParam = params.get(keyLang)
        const locale = langQueryParam || defaultLang;

        this._localeService.init(locale);

        this._config = reactive({
            locale: locale,
        })
    }

    get config() {
        return this._config
    }




}