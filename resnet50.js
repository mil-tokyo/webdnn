/******/ (function(modules) { // webpackBootstrap
/******/ 	// The module cache
/******/ 	var installedModules = {};
/******/
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/
/******/ 		// Check if module is in cache
/******/ 		if(installedModules[moduleId]) {
/******/ 			return installedModules[moduleId].exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = installedModules[moduleId] = {
/******/ 			i: moduleId,
/******/ 			l: false,
/******/ 			exports: {}
/******/ 		};
/******/
/******/ 		// Execute the module function
/******/ 		modules[moduleId].call(module.exports, module, module.exports, __webpack_require__);
/******/
/******/ 		// Flag the module as loaded
/******/ 		module.l = true;
/******/
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/
/******/
/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = modules;
/******/
/******/ 	// expose the module cache
/******/ 	__webpack_require__.c = installedModules;
/******/
/******/ 	// identity function for calling harmony imports with the correct context
/******/ 	__webpack_require__.i = function(value) { return value; };
/******/
/******/ 	// define getter function for harmony exports
/******/ 	__webpack_require__.d = function(exports, name, getter) {
/******/ 		if(!__webpack_require__.o(exports, name)) {
/******/ 			Object.defineProperty(exports, name, {
/******/ 				configurable: false,
/******/ 				enumerable: true,
/******/ 				get: getter
/******/ 			});
/******/ 		}
/******/ 	};
/******/
/******/ 	// getDefaultExport function for compatibility with non-harmony modules
/******/ 	__webpack_require__.n = function(module) {
/******/ 		var getter = module && module.__esModule ?
/******/ 			function getDefault() { return module['default']; } :
/******/ 			function getModuleExports() { return module; };
/******/ 		__webpack_require__.d(getter, 'a', getter);
/******/ 		return getter;
/******/ 	};
/******/
/******/ 	// Object.prototype.hasOwnProperty.call
/******/ 	__webpack_require__.o = function(object, property) { return Object.prototype.hasOwnProperty.call(object, property); };
/******/
/******/ 	// __webpack_public_path__
/******/ 	__webpack_require__.p = "";
/******/
/******/ 	// Load entry module and return exports
/******/ 	return __webpack_require__(__webpack_require__.s = 11);
/******/ })
/************************************************************************/
/******/ ([
/* 0 */
/***/ (function(module, exports) {

(function (i, s, o, g, r, a, m) {
	i['GoogleAnalyticsObject'] = r;
	i[r] = i[r] || function () {
			(i[r].q = i[r].q || []).push(arguments)
		}, i[r].l = 1 * new Date();
	a = s.createElement(o),
		m = s.getElementsByTagName(o)[0];
	a.async = 1;
	a.src = g;
	m.parentNode.insertBefore(a, m)
})(window, document, 'script', 'https://www.google-analytics.com/analytics.js', 'ga');

ga('create', 'UA-100057100-1', 'auto');
ga('send', 'pageview');


/***/ }),
/* 1 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

Object.defineProperty(exports, "__esModule", { value: true });
var progress_bar_1 = __webpack_require__(2);
var InitializingView = (function () {
    function InitializingView(base) {
        this.base = base;
        var message = base.querySelector('.InitializingView-Message');
        if (!message)
            throw Error('.InitializingView-Message not found');
        this.message = message;
        var progressBarInner = base.querySelector('.ProgressBar-Inner');
        if (!progressBarInner)
            throw Error('.ProgressBar-Inner not found');
        this.progressBar = new progress_bar_1.default(progressBarInner);
    }
    InitializingView.prototype.updateProgress = function (ratio) {
        this.progressBar.update(ratio);
    };
    InitializingView.prototype.updateMessage = function (message) {
        this.message.textContent = message;
    };
    InitializingView.prototype.remove = function () {
        if (this.base.parentNode) {
            this.base.parentNode.removeChild(this.base);
        }
    };
    return InitializingView;
}());
exports.default = InitializingView;


/***/ }),
/* 2 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

Object.defineProperty(exports, "__esModule", { value: true });
var ProgressBar = (function () {
    function ProgressBar(bar) {
        this.bar = bar;
    }
    ProgressBar.prototype.update = function (ratio) {
        this.bar.style.width = Math.min(Math.max(ratio, 0), 1) * 100 + "%";
    };
    return ProgressBar;
}());
exports.default = ProgressBar;


/***/ }),
/* 3 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : new P(function (resolve) { resolve(result.value); }).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g;
    return g = { next: verb(0), "throw": verb(1), "return": verb(2) }, typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (_) try {
            if (f = 1, y && (t = y[op[0] & 2 ? "return" : op[0] ? "throw" : "next"]) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [0, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
Object.defineProperty(exports, "__esModule", { value: true });
var ImagePicker = (function () {
    function ImagePicker(input, context) {
        var _this = this;
        this.input = input;
        this.context = context;
        this.input.addEventListener('change', function (ev) { return _this.onInputChange(ev); });
    }
    ImagePicker.prototype.onInputChange = function (ev) {
        var _this = this;
        if (!this.input || !this.input.files || !this.input.files[0])
            return;
        this.loadByFile(this.input.files[0])
            .then(function () {
            if (_this.onload) {
                _this.onload();
            }
        })
            .catch(function (err) {
            throw err;
        });
    };
    ImagePicker.prototype.loadByFile = function (file) {
        return __awaiter(this, void 0, void 0, function () {
            var _this = this;
            var reader;
            return __generator(this, function (_a) {
                reader = new FileReader();
                return [2, new Promise(function (resolve) {
                        reader.onload = function (ev) { return _this.loadByUrl(reader.result); };
                        reader.readAsDataURL(file);
                    })];
            });
        });
    };
    ImagePicker.prototype.loadByUrl = function (url) {
        return __awaiter(this, void 0, void 0, function () {
            var image, err_1;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        _a.trys.push([0, 2, , 3]);
                        return [4, this.fetchImageAsync(url)];
                    case 1:
                        image = _a.sent();
                        return [3, 3];
                    case 2:
                        err_1 = _a.sent();
                        throw err_1;
                    case 3:
                        this.setImageToCanvas(image);
                        if (this.onload) {
                            this.onload();
                        }
                        return [2];
                }
            });
        });
    };
    ImagePicker.prototype.setImageToCanvas = function (image) {
        this.context.drawImage(image, 0, 0, image.width, image.height, 0, 0, this.context.canvas.width, this.context.canvas.height);
    };
    ImagePicker.prototype.fetchImageAsync = function (url) {
        var image = new Image();
        return new Promise(function (resolve) {
            image.onload = function () { return resolve(image); };
            image.src = url;
        });
    };
    return ImagePicker;
}());
exports.default = ImagePicker;


/***/ }),
/* 4 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

Object.defineProperty(exports, "__esModule", { value: true });
var Labels = [
    "tench",
    "goldfish",
    "great white shark",
    "tiger shark",
    "hammerhead",
    "electric ray",
    "stingray",
    "cock",
    "hen",
    "ostrich",
    "brambling",
    "goldfinch",
    "house finch",
    "junco",
    "indigo bunting",
    "robin",
    "bulbul",
    "jay",
    "magpie",
    "chickadee",
    "water ouzel",
    "kite",
    "bald eagle",
    "vulture",
    "great grey owl",
    "European fire salamander",
    "common newt",
    "eft",
    "spotted salamander",
    "axolotl",
    "bullfrog",
    "tree frog",
    "tailed frog",
    "loggerhead",
    "leatherback turtle",
    "mud turtle",
    "terrapin",
    "box turtle",
    "banded gecko",
    "common iguana",
    "American chameleon",
    "whiptail",
    "agama",
    "frilled lizard",
    "alligator lizard",
    "Gila monster",
    "green lizard",
    "African chameleon",
    "Komodo dragon",
    "African crocodile",
    "American alligator",
    "triceratops",
    "thunder snake",
    "ringneck snake",
    "hognose snake",
    "green snake",
    "king snake",
    "garter snake",
    "water snake",
    "vine snake",
    "night snake",
    "boa constrictor",
    "rock python",
    "Indian cobra",
    "green mamba",
    "sea snake",
    "horned viper",
    "diamondback",
    "sidewinder",
    "trilobite",
    "harvestman",
    "scorpion",
    "black and gold garden spider",
    "barn spider",
    "garden spider",
    "black widow",
    "tarantula",
    "wolf spider",
    "tick",
    "centipede",
    "black grouse",
    "ptarmigan",
    "ruffed grouse",
    "prairie chicken",
    "peacock",
    "quail",
    "partridge",
    "African grey",
    "macaw",
    "sulphur-crested cockatoo",
    "lorikeet",
    "coucal",
    "bee eater",
    "hornbill",
    "hummingbird",
    "jacamar",
    "toucan",
    "drake",
    "red-breasted merganser",
    "goose",
    "black swan",
    "tusker",
    "echidna",
    "platypus",
    "wallaby",
    "koala",
    "wombat",
    "jellyfish",
    "sea anemone",
    "brain coral",
    "flatworm",
    "nematode",
    "conch",
    "snail",
    "slug",
    "sea slug",
    "chiton",
    "chambered nautilus",
    "Dungeness crab",
    "rock crab",
    "fiddler crab",
    "king crab",
    "American lobster",
    "spiny lobster",
    "crayfish",
    "hermit crab",
    "isopod",
    "white stork",
    "black stork",
    "spoonbill",
    "flamingo",
    "little blue heron",
    "American egret",
    "bittern",
    "crane",
    "limpkin",
    "European gallinule",
    "American coot",
    "bustard",
    "ruddy turnstone",
    "red-backed sandpiper",
    "redshank",
    "dowitcher",
    "oystercatcher",
    "pelican",
    "king penguin",
    "albatross",
    "grey whale",
    "killer whale",
    "dugong",
    "sea lion",
    "Chihuahua",
    "Japanese spaniel",
    "Maltese dog",
    "Pekinese",
    "Shih-Tzu",
    "Blenheim spaniel",
    "papillon",
    "toy terrier",
    "Rhodesian ridgeback",
    "Afghan hound",
    "basset",
    "beagle",
    "bloodhound",
    "bluetick",
    "black-and-tan coonhound",
    "Walker hound",
    "English foxhound",
    "redbone",
    "borzoi",
    "Irish wolfhound",
    "Italian greyhound",
    "whippet",
    "Ibizan hound",
    "Norwegian elkhound",
    "otterhound",
    "Saluki",
    "Scottish deerhound",
    "Weimaraner",
    "Staffordshire bullterrier",
    "American Staffordshire terrier",
    "Bedlington terrier",
    "Border terrier",
    "Kerry blue terrier",
    "Irish terrier",
    "Norfolk terrier",
    "Norwich terrier",
    "Yorkshire terrier",
    "wire-haired fox terrier",
    "Lakeland terrier",
    "Sealyham terrier",
    "Airedale",
    "cairn",
    "Australian terrier",
    "Dandie Dinmont",
    "Boston bull",
    "miniature schnauzer",
    "giant schnauzer",
    "standard schnauzer",
    "Scotch terrier",
    "Tibetan terrier",
    "silky terrier",
    "soft-coated wheaten terrier",
    "West Highland white terrier",
    "Lhasa",
    "flat-coated retriever",
    "curly-coated retriever",
    "golden retriever",
    "Labrador retriever",
    "Chesapeake Bay retriever",
    "German short-haired pointer",
    "vizsla",
    "English setter",
    "Irish setter",
    "Gordon setter",
    "Brittany spaniel",
    "clumber",
    "English springer",
    "Welsh springer spaniel",
    "cocker spaniel",
    "Sussex spaniel",
    "Irish water spaniel",
    "kuvasz",
    "schipperke",
    "groenendael",
    "malinois",
    "briard",
    "kelpie",
    "komondor",
    "Old English sheepdog",
    "Shetland sheepdog",
    "collie",
    "Border collie",
    "Bouvier des Flandres",
    "Rottweiler",
    "German shepherd",
    "Doberman",
    "miniature pinscher",
    "Greater Swiss Mountain dog",
    "Bernese mountain dog",
    "Appenzeller",
    "EntleBucher",
    "boxer",
    "bull mastiff",
    "Tibetan mastiff",
    "French bulldog",
    "Great Dane",
    "Saint Bernard",
    "Eskimo dog",
    "malamute",
    "Siberian husky",
    "dalmatian",
    "affenpinscher",
    "basenji",
    "pug",
    "Leonberg",
    "Newfoundland",
    "Great Pyrenees",
    "Samoyed",
    "Pomeranian",
    "chow",
    "keeshond",
    "Brabancon griffon",
    "Pembroke",
    "Cardigan",
    "toy poodle",
    "miniature poodle",
    "standard poodle",
    "Mexican hairless",
    "timber wolf",
    "white wolf",
    "red wolf",
    "coyote",
    "dingo",
    "dhole",
    "African hunting dog",
    "hyena",
    "red fox",
    "kit fox",
    "Arctic fox",
    "grey fox",
    "tabby",
    "tiger cat",
    "Persian cat",
    "Siamese cat",
    "Egyptian cat",
    "cougar",
    "lynx",
    "leopard",
    "snow leopard",
    "jaguar",
    "lion",
    "tiger",
    "cheetah",
    "brown bear",
    "American black bear",
    "ice bear",
    "sloth bear",
    "mongoose",
    "meerkat",
    "tiger beetle",
    "ladybug",
    "ground beetle",
    "long-horned beetle",
    "leaf beetle",
    "dung beetle",
    "rhinoceros beetle",
    "weevil",
    "fly",
    "bee",
    "ant",
    "grasshopper",
    "cricket",
    "walking stick",
    "cockroach",
    "mantis",
    "cicada",
    "leafhopper",
    "lacewing",
    "dragonfly",
    "damselfly",
    "admiral",
    "ringlet",
    "monarch",
    "cabbage butterfly",
    "sulphur butterfly",
    "lycaenid",
    "starfish",
    "sea urchin",
    "sea cucumber",
    "wood rabbit",
    "hare",
    "Angora",
    "hamster",
    "porcupine",
    "fox squirrel",
    "marmot",
    "beaver",
    "guinea pig",
    "sorrel",
    "zebra",
    "hog",
    "wild boar",
    "warthog",
    "hippopotamus",
    "ox",
    "water buffalo",
    "bison",
    "ram",
    "bighorn",
    "ibex",
    "hartebeest",
    "impala",
    "gazelle",
    "Arabian camel",
    "llama",
    "weasel",
    "mink",
    "polecat",
    "black-footed ferret",
    "otter",
    "skunk",
    "badger",
    "armadillo",
    "three-toed sloth",
    "orangutan",
    "gorilla",
    "chimpanzee",
    "gibbon",
    "siamang",
    "guenon",
    "patas",
    "baboon",
    "macaque",
    "langur",
    "colobus",
    "proboscis monkey",
    "marmoset",
    "capuchin",
    "howler monkey",
    "titi",
    "spider monkey",
    "squirrel monkey",
    "Madagascar cat",
    "indri",
    "Indian elephant",
    "African elephant",
    "lesser panda",
    "giant panda",
    "barracouta",
    "eel",
    "coho",
    "rock beauty",
    "anemone fish",
    "sturgeon",
    "gar",
    "lionfish",
    "puffer",
    "abacus",
    "abaya",
    "academic gown",
    "accordion",
    "acoustic guitar",
    "aircraft carrier",
    "airliner",
    "airship",
    "altar",
    "ambulance",
    "amphibian",
    "analog clock",
    "apiary",
    "apron",
    "ashcan",
    "assault rifle",
    "backpack",
    "bakery",
    "balance beam",
    "balloon",
    "ballpoint",
    "Band Aid",
    "banjo",
    "bannister",
    "barbell",
    "barber chair",
    "barbershop",
    "barn",
    "barometer",
    "barrel",
    "barrow",
    "baseball",
    "basketball",
    "bassinet",
    "bassoon",
    "bathing cap",
    "bath towel",
    "bathtub",
    "beach wagon",
    "beacon",
    "beaker",
    "bearskin",
    "beer bottle",
    "beer glass",
    "bell cote",
    "bib",
    "bicycle-built-for-two",
    "bikini",
    "binder",
    "binoculars",
    "birdhouse",
    "boathouse",
    "bobsled",
    "bolo tie",
    "bonnet",
    "bookcase",
    "bookshop",
    "bottlecap",
    "bow",
    "bow tie",
    "brass",
    "brassiere",
    "breakwater",
    "breastplate",
    "broom",
    "bucket",
    "buckle",
    "bulletproof vest",
    "bullet train",
    "butcher shop",
    "cab",
    "caldron",
    "candle",
    "cannon",
    "canoe",
    "can opener",
    "cardigan",
    "car mirror",
    "carousel",
    "carpenter's kit",
    "carton",
    "car wheel",
    "cash machine",
    "cassette",
    "cassette player",
    "castle",
    "catamaran",
    "CD player",
    "cello",
    "cellular telephone",
    "chain",
    "chainlink fence",
    "chain mail",
    "chain saw",
    "chest",
    "chiffonier",
    "chime",
    "china cabinet",
    "Christmas stocking",
    "church",
    "cinema",
    "cleaver",
    "cliff dwelling",
    "cloak",
    "clog",
    "cocktail shaker",
    "coffee mug",
    "coffeepot",
    "coil",
    "combination lock",
    "computer keyboard",
    "confectionery",
    "container ship",
    "convertible",
    "corkscrew",
    "cornet",
    "cowboy boot",
    "cowboy hat",
    "cradle",
    "crane",
    "crash helmet",
    "crate",
    "crib",
    "Crock Pot",
    "croquet ball",
    "crutch",
    "cuirass",
    "dam",
    "desk",
    "desktop computer",
    "dial telephone",
    "diaper",
    "digital clock",
    "digital watch",
    "dining table",
    "dishrag",
    "dishwasher",
    "disk brake",
    "dock",
    "dogsled",
    "dome",
    "doormat",
    "drilling platform",
    "drum",
    "drumstick",
    "dumbbell",
    "Dutch oven",
    "electric fan",
    "electric guitar",
    "electric locomotive",
    "entertainment center",
    "envelope",
    "espresso maker",
    "face powder",
    "feather boa",
    "file",
    "fireboat",
    "fire engine",
    "fire screen",
    "flagpole",
    "flute",
    "folding chair",
    "football helmet",
    "forklift",
    "fountain",
    "fountain pen",
    "four-poster",
    "freight car",
    "French horn",
    "frying pan",
    "fur coat",
    "garbage truck",
    "gasmask",
    "gas pump",
    "goblet",
    "go-kart",
    "golf ball",
    "golfcart",
    "gondola",
    "gong",
    "gown",
    "grand piano",
    "greenhouse",
    "grille",
    "grocery store",
    "guillotine",
    "hair slide",
    "hair spray",
    "half track",
    "hammer",
    "hamper",
    "hand blower",
    "hand-held computer",
    "handkerchief",
    "hard disc",
    "harmonica",
    "harp",
    "harvester",
    "hatchet",
    "holster",
    "home theater",
    "honeycomb",
    "hook",
    "hoopskirt",
    "horizontal bar",
    "horse cart",
    "hourglass",
    "iPod",
    "iron",
    "jack-o'-lantern",
    "jean",
    "jeep",
    "jersey",
    "jigsaw puzzle",
    "jinrikisha",
    "joystick",
    "kimono",
    "knee pad",
    "knot",
    "lab coat",
    "ladle",
    "lampshade",
    "laptop",
    "lawn mower",
    "lens cap",
    "letter opener",
    "library",
    "lifeboat",
    "lighter",
    "limousine",
    "liner",
    "lipstick",
    "Loafer",
    "lotion",
    "loudspeaker",
    "loupe",
    "lumbermill",
    "magnetic compass",
    "mailbag",
    "mailbox",
    "maillot",
    "maillot",
    "manhole cover",
    "maraca",
    "marimba",
    "mask",
    "matchstick",
    "maypole",
    "maze",
    "measuring cup",
    "medicine chest",
    "megalith",
    "microphone",
    "microwave",
    "military uniform",
    "milk can",
    "minibus",
    "miniskirt",
    "minivan",
    "missile",
    "mitten",
    "mixing bowl",
    "mobile home",
    "Model T",
    "modem",
    "monastery",
    "monitor",
    "moped",
    "mortar",
    "mortarboard",
    "mosque",
    "mosquito net",
    "motor scooter",
    "mountain bike",
    "mountain tent",
    "mouse",
    "mousetrap",
    "moving van",
    "muzzle",
    "nail",
    "neck brace",
    "necklace",
    "nipple",
    "notebook",
    "obelisk",
    "oboe",
    "ocarina",
    "odometer",
    "oil filter",
    "organ",
    "oscilloscope",
    "overskirt",
    "oxcart",
    "oxygen mask",
    "packet",
    "paddle",
    "paddlewheel",
    "padlock",
    "paintbrush",
    "pajama",
    "palace",
    "panpipe",
    "paper towel",
    "parachute",
    "parallel bars",
    "park bench",
    "parking meter",
    "passenger car",
    "patio",
    "pay-phone",
    "pedestal",
    "pencil box",
    "pencil sharpener",
    "perfume",
    "Petri dish",
    "photocopier",
    "pick",
    "pickelhaube",
    "picket fence",
    "pickup",
    "pier",
    "piggy bank",
    "pill bottle",
    "pillow",
    "ping-pong ball",
    "pinwheel",
    "pirate",
    "pitcher",
    "plane",
    "planetarium",
    "plastic bag",
    "plate rack",
    "plow",
    "plunger",
    "Polaroid camera",
    "pole",
    "police van",
    "poncho",
    "pool table",
    "pop bottle",
    "pot",
    "potter's wheel",
    "power drill",
    "prayer rug",
    "printer",
    "prison",
    "projectile",
    "projector",
    "puck",
    "punching bag",
    "purse",
    "quill",
    "quilt",
    "racer",
    "racket",
    "radiator",
    "radio",
    "radio telescope",
    "rain barrel",
    "recreational vehicle",
    "reel",
    "reflex camera",
    "refrigerator",
    "remote control",
    "restaurant",
    "revolver",
    "rifle",
    "rocking chair",
    "rotisserie",
    "rubber eraser",
    "rugby ball",
    "rule",
    "running shoe",
    "safe",
    "safety pin",
    "saltshaker",
    "sandal",
    "sarong",
    "sax",
    "scabbard",
    "scale",
    "school bus",
    "schooner",
    "scoreboard",
    "screen",
    "screw",
    "screwdriver",
    "seat belt",
    "sewing machine",
    "shield",
    "shoe shop",
    "shoji",
    "shopping basket",
    "shopping cart",
    "shovel",
    "shower cap",
    "shower curtain",
    "ski",
    "ski mask",
    "sleeping bag",
    "slide rule",
    "sliding door",
    "slot",
    "snorkel",
    "snowmobile",
    "snowplow",
    "soap dispenser",
    "soccer ball",
    "sock",
    "solar dish",
    "sombrero",
    "soup bowl",
    "space bar",
    "space heater",
    "space shuttle",
    "spatula",
    "speedboat",
    "spider web",
    "spindle",
    "sports car",
    "spotlight",
    "stage",
    "steam locomotive",
    "steel arch bridge",
    "steel drum",
    "stethoscope",
    "stole",
    "stone wall",
    "stopwatch",
    "stove",
    "strainer",
    "streetcar",
    "stretcher",
    "studio couch",
    "stupa",
    "submarine",
    "suit",
    "sundial",
    "sunglass",
    "sunglasses",
    "sunscreen",
    "suspension bridge",
    "swab",
    "sweatshirt",
    "swimming trunks",
    "swing",
    "switch",
    "syringe",
    "table lamp",
    "tank",
    "tape player",
    "teapot",
    "teddy",
    "television",
    "tennis ball",
    "thatch",
    "theater curtain",
    "thimble",
    "thresher",
    "throne",
    "tile roof",
    "toaster",
    "tobacco shop",
    "toilet seat",
    "torch",
    "totem pole",
    "tow truck",
    "toyshop",
    "tractor",
    "trailer truck",
    "tray",
    "trench coat",
    "tricycle",
    "trimaran",
    "tripod",
    "triumphal arch",
    "trolleybus",
    "trombone",
    "tub",
    "turnstile",
    "typewriter keyboard",
    "umbrella",
    "unicycle",
    "upright",
    "vacuum",
    "vase",
    "vault",
    "velvet",
    "vending machine",
    "vestment",
    "viaduct",
    "violin",
    "volleyball",
    "waffle iron",
    "wall clock",
    "wallet",
    "wardrobe",
    "warplane",
    "washbasin",
    "washer",
    "water bottle",
    "water jug",
    "water tower",
    "whiskey jug",
    "whistle",
    "wig",
    "window screen",
    "window shade",
    "Windsor tie",
    "wine bottle",
    "wing",
    "wok",
    "wooden spoon",
    "wool",
    "worm fence",
    "wreck",
    "yawl",
    "yurt",
    "web site",
    "comic book",
    "crossword puzzle",
    "street sign",
    "traffic light",
    "book jacket",
    "menu",
    "plate",
    "guacamole",
    "consomme",
    "hot pot",
    "trifle",
    "ice cream",
    "ice lolly",
    "French loaf",
    "bagel",
    "pretzel",
    "cheeseburger",
    "hotdog",
    "mashed potato",
    "head cabbage",
    "broccoli",
    "cauliflower",
    "zucchini",
    "spaghetti squash",
    "acorn squash",
    "butternut squash",
    "cucumber",
    "artichoke",
    "bell pepper",
    "cardoon",
    "mushroom",
    "Granny Smith",
    "strawberry",
    "orange",
    "lemon",
    "fig",
    "pineapple",
    "banana",
    "jackfruit",
    "custard apple",
    "pomegranate",
    "hay",
    "carbonara",
    "chocolate sauce",
    "dough",
    "meat loaf",
    "pizza",
    "potpie",
    "burrito",
    "red wine",
    "espresso",
    "cup",
    "eggnog",
    "alp",
    "bubble",
    "cliff",
    "coral reef",
    "geyser",
    "lakeside",
    "promontory",
    "sandbar",
    "seashore",
    "valley",
    "volcano",
    "ballplayer",
    "groom",
    "scuba diver",
    "rapeseed",
    "daisy",
    "yellow lady's slipper",
    "corn",
    "acorn",
    "hip",
    "buckeye",
    "coral fungus",
    "agaric",
    "gyromitra",
    "stinkhorn",
    "earthstar",
    "hen-of-the-woods",
    "bolete",
    "ear",
    "toilet tissue"
];
exports.default = Labels;


/***/ }),
/* 5 */,
/* 6 */,
/* 7 */,
/* 8 */
/***/ (function(module, exports) {

// removed by extract-text-webpack-plugin

/***/ }),
/* 9 */,
/* 10 */,
/* 11 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : new P(function (resolve) { resolve(result.value); }).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g;
    return g = { next: verb(0), "throw": verb(1), "return": verb(2) }, typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (_) try {
            if (f = 1, y && (t = y[op[0] & 2 ? "return" : op[0] ? "throw" : "next"]) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [0, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
Object.defineProperty(exports, "__esModule", { value: true });
__webpack_require__(8);
__webpack_require__(0);
var image_picker_1 = __webpack_require__(3);
var imagenet_labels_1 = __webpack_require__(4);
var initializing_view_1 = __webpack_require__(1);
var KEY_WEBGPU_LAST_STATUS = 'webgpu_last_status';
var KEY_FLAG_WEBGPU_DISABLED_ALERT = 'flag_webgpu_disabled_alert';
var NUM_RANDOM_IMAGE = 6;
var FLAG_CHROME_ANDROID = false;
var State;
(function (State) {
    State[State["INITIALIZING"] = 0] = "INITIALIZING";
    State[State["NO_IMAGE"] = 1] = "NO_IMAGE";
    State[State["STAND_BY"] = 2] = "STAND_BY";
    State[State["RUNNING"] = 3] = "RUNNING";
    State[State["ERROR"] = 4] = "ERROR";
})(State || (State = {}));
function softMax(arr) {
    var exps = [];
    var sum = 0;
    for (var i = 0; i < arr.length; i++) {
        var e = Math.exp(arr[i]);
        sum += e;
        exps[i] = e;
    }
    for (var i = 0; i < arr.length; i++) {
        exps[i] /= sum;
    }
    return exps;
}
var App = new (function () {
    function class_1() {
        this.lastStatus = '';
    }
    class_1.prototype.initialize = function () {
        return __awaiter(this, void 0, void 0, function () {
            var _this = this;
            var canvas, context, runButton, loadRandomButton, messageView, predictedItems, i, item, resultLabel, resultBar, resultProbability, launchView, initializingViewBase, initializingView, availability, _a, _b;
            return __generator(this, function (_c) {
                switch (_c.label) {
                    case 0:
                        this.setState(State.INITIALIZING);
                        this.randomImageIndex = Math.floor(Math.random() * NUM_RANDOM_IMAGE);
                        canvas = document.getElementById('canvas');
                        context = canvas.getContext('2d');
                        if (!context)
                            throw new Error('Context is null');
                        this.context = context;
                        this.picker = new image_picker_1.default(document.getElementById('imageInput'), context);
                        this.picker.onload = function () {
                            _this.setState(State.STAND_BY);
                        };
                        runButton = document.getElementById('runButton');
                        if (!runButton)
                            throw Error('#runButton is not found.');
                        this.runButton = runButton;
                        this.runButton.addEventListener('click', function () { return App.predict(); });
                        loadRandomButton = document.getElementById('loadRandomButton');
                        if (!loadRandomButton)
                            throw Error('#loadRandomButton is not found.');
                        loadRandomButton.addEventListener('click', function () { return App.loadRandomImage(); });
                        messageView = document.getElementById('message');
                        if (!messageView)
                            throw Error('#message is not found.');
                        this.messageView = messageView;
                        this.resultLabels = [];
                        this.resultBars = [];
                        this.resultProbabilities = [];
                        predictedItems = document.querySelectorAll('.ResultItem');
                        if (predictedItems.length != 10)
                            throw Error('# of .ResultItem must be 10.');
                        for (i = 0; i < 10; i++) {
                            item = predictedItems[i];
                            resultLabel = item.querySelector('.ResultItem-Label');
                            if (!resultLabel)
                                throw Error('.ResultItem-Label is not found.');
                            this.resultLabels.push(resultLabel);
                            resultBar = item.querySelector('.ResultItem-Bar');
                            if (!resultBar)
                                throw Error('.ResultItem-Bar is not found.');
                            this.resultBars.push(resultBar);
                            resultProbability = item.querySelector('.ResultItem-Probability');
                            if (!resultProbability)
                                throw Error('.ResultItem-Probability is not found.');
                            this.resultProbabilities.push(resultProbability);
                        }
                        launchView = document.getElementById('launchView');
                        if (launchView && launchView.parentNode) {
                            launchView.parentNode.removeChild(launchView);
                            launchView = null;
                        }
                        initializingViewBase = document.getElementById('initializingView');
                        if (!initializingViewBase)
                            throw Error('#initializingView is not found');
                        initializingView = new initializing_view_1.default(initializingViewBase);
                        if (FLAG_CHROME_ANDROID) {
                            initializingView.updateMessage('Sorry, but this application can\'t work on Chrome for Android.');
                            return [2];
                        }
                        else {
                            console.log(navigator.userAgent);
                        }
                        availability = WebDNN.getBackendAvailability();
                        if (availability.status['webgpu']) {
                            this.lastStatus = localStorage.getItem(KEY_WEBGPU_LAST_STATUS) || 'none';
                            switch (this.lastStatus) {
                                case 'none':
                                    break;
                                case 'running':
                                case 'crashed':
                                    availability.status['webgpu'] = false;
                                    availability.defaultOrder.splice(availability.defaultOrder.indexOf('webgpu'), 1);
                                    localStorage.setItem(KEY_WEBGPU_LAST_STATUS, 'crashed');
                                    console.warn('This browser supports WebGPU. However, it was crashed at last execution with WebGPU. Therefore, WebDNN disabled WebGPU backend temporally.');
                                    if (!localStorage.getItem(KEY_FLAG_WEBGPU_DISABLED_ALERT)) {
                                        alert('This browser supports WebGPU. However, it was crashed at last execution with WebGPU. \n\nTherefore, WebDNN disabled WebGPU backend temporally.');
                                        localStorage.setItem(KEY_FLAG_WEBGPU_DISABLED_ALERT, '1');
                                    }
                                    break;
                                case 'completed':
                                    break;
                            }
                        }
                        initializingView.updateMessage('Load label data');
                        this.labels = imagenet_labels_1.default;
                        initializingView.updateMessage('Load model data');
                        return [4, WebDNN.init(availability.defaultOrder)];
                    case 1:
                        _c.sent();
                        this.runner = WebDNN.gpu.createDescriptorRunner();
                        return [4, this.runner.load('./models/resnet50', function (loaded, total) { return initializingView.updateProgress(loaded / total); })];
                    case 2:
                        _c.sent();
                        _a = this;
                        return [4, this.runner.getInputViews()];
                    case 3:
                        _a.inputView = (_c.sent())[0];
                        _b = this;
                        return [4, this.runner.getOutputViews()];
                    case 4:
                        _b.outputView = (_c.sent())[0];
                        initializingView.remove();
                        this.setState(State.NO_IMAGE);
                        this.loadRandomImage();
                        return [2];
                }
            });
        });
    };
    class_1.prototype.setMessage = function (message) {
        if (this.messageView) {
            this.messageView.textContent = message;
        }
    };
    class_1.prototype.setState = function (state) {
        this.state = state;
        switch (state) {
            case State.INITIALIZING:
                this.setMessage('Initializing...');
                if (this.runButton) {
                    this.runButton.textContent = 'Initializing...';
                    this.runButton.disabled = true;
                }
                break;
            case State.NO_IMAGE:
                this.setMessage('Select an image, and click "Run" button.');
                if (this.runButton) {
                    this.runButton.textContent = 'Run';
                    this.runButton.disabled = true;
                }
                break;
            case State.STAND_BY:
                this.setMessage("Ready(backend: " + this.runner.backend + ")");
                if (this.runButton) {
                    this.runButton.textContent = 'Run';
                    this.runButton.disabled = false;
                }
                break;
            case State.RUNNING:
                this.setMessage('Running...');
                if (this.runButton) {
                    this.runButton.textContent = 'Running...';
                    this.runButton.disabled = true;
                }
                break;
            case State.ERROR:
                this.setMessage('Error');
                if (this.runButton) {
                    this.runButton.textContent = 'Error';
                    this.runButton.disabled = true;
                }
                break;
        }
    };
    class_1.prototype.setInputImageData = function () {
        var w = this.context.canvas.width;
        var h = this.context.canvas.height;
        var imageData = this.context.getImageData(0, 0, w, h);
        var pixelData = imageData.data;
        for (var y = 0; y < h; y++) {
            for (var x = 0; x < w; x++) {
                this.inputView[(y * w + x) * 3] = pixelData[(y * w + x) * 4 + 2] - 103.939;
                this.inputView[(y * w + x) * 3 + 1] = pixelData[(y * w + x) * 4 + 1] - 116.779;
                this.inputView[(y * w + x) * 3 + 2] = pixelData[(y * w + x) * 4] - 123.68;
            }
        }
    };
    class_1.prototype.loadRandomImage = function () {
        this.randomImageIndex = (this.randomImageIndex + 1) % NUM_RANDOM_IMAGE;
        this.picker.loadByUrl("./assets/images/" + this.randomImageIndex + ".png");
    };
    class_1.prototype.predict = function () {
        return __awaiter(this, void 0, void 0, function () {
            var _this = this;
            var start, computationTime, output, i, probability, top5;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        this.setState(State.RUNNING);
                        this.setInputImageData();
                        if (this.runner.backend === 'webgpu' && this.lastStatus === 'none') {
                            localStorage.setItem(KEY_WEBGPU_LAST_STATUS, 'running');
                            this.lastStatus = 'running';
                        }
                        start = performance.now();
                        return [4, this.runner.run()];
                    case 1:
                        _a.sent();
                        computationTime = performance.now() - start;
                        if (this.runner.backend === 'webgpu' && this.lastStatus === 'running') {
                            localStorage.setItem(KEY_WEBGPU_LAST_STATUS, 'completed');
                            this.lastStatus = 'completed';
                        }
                        output = [];
                        for (i = 0; i < this.outputView.length; i++) {
                            output.push(this.outputView[i]);
                        }
                        probability = softMax(output);
                        top5 = WebDNN.Math.argmax(probability.slice(0), 10);
                        top5.forEach(function (labelId, i) {
                            _this.resultProbabilities[i].textContent = (probability[labelId] * 100).toFixed(1) + "%";
                            _this.resultProbabilities[i].style.opacity = '1';
                            _this.resultBars[i].style.width = (probability[labelId] * 100) + "%";
                            _this.resultBars[i].style.opacity = '' + (0.3 + probability[labelId] * 0.7);
                            _this.resultLabels[i].textContent = _this.labels[labelId];
                            _this.resultLabels[i].style.opacity = '1';
                        });
                        this.setState(State.STAND_BY);
                        this.setMessage("Computation Time: " + computationTime.toFixed(2) + " [ms]");
                        return [2];
                }
            });
        });
    };
    return class_1;
}());
window.onload = function () {
    FLAG_CHROME_ANDROID = ((/Android(.*)Chrome/).test(navigator.userAgent));
    WebDNN.registerTransformDelegate(function (url) {
        var ma = url.match(/([^/]+)(?:\?.*)?$/);
        if (ma) {
            return "https://mil-tokyo.github.io/webdnn-data/models/resnet50/" + ma[1] + "?raw=true";
        }
        else {
            return url;
        }
    });
    var runAppButton = document.getElementById('runAppButton');
    if (!runAppButton)
        throw Error('#runAppButton is not found');
    runAppButton.addEventListener('click', function () { return App.initialize(); });
    if (location.search == '?run=1') {
        App.initialize();
    }
};


/***/ })
/******/ ]);