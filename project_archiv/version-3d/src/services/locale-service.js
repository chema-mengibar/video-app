import EsDictionary from './locale/locale-es.json';
import EnDictionary from './locale/locale-en.json';


export default class LocaleService {

    _dict = null;
    _locales = ['es', 'en'];

    constructor() {
 
    }

    get locales() {
        return this._locales 
    }


    init(locale) {
        if (locale === 'es') {
            this._dict = { ...EsDictionary };
        }
        else if (locale === 'en') {
            this._dict = { ...EnDictionary };
        }
    }


    t() {
        return (labelKey) => this._dict[labelKey];
    }

    T() {
        return (labelKeys) => {
            const o = {}
            labelKeys.forEach(labelKey => {
                o[labelKey] = this._dict[labelKey];
            })
            return o;
        }
    }

    D() {
        return this._dict
    }





}