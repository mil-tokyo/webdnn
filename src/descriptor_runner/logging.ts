declare global {
  interface Window {
    WebDNNLoggingManagerInstance: WebDNNLogging;
  }
}

class WebDNNLogger {
  constructor(public category: string, public logging: WebDNNLogging) {}
  debug(message?: any, ...optionalParams: any[]) {
    this.logging.emit(
      this.category,
      WebDNNLogging.DEBUG,
      message,
      optionalParams
    );
  }
  info(message?: any, ...optionalParams: any[]) {
    this.logging.emit(
      this.category,
      WebDNNLogging.INFO,
      message,
      optionalParams
    );
  }
  warn(message?: any, ...optionalParams: any[]) {
    this.logging.emit(
      this.category,
      WebDNNLogging.WARN,
      message,
      optionalParams
    );
  }
  error(message?: any, ...optionalParams: any[]) {
    this.logging.emit(
      this.category,
      WebDNNLogging.ERROR,
      message,
      optionalParams
    );
  }
  fatal(message?: any, ...optionalParams: any[]) {
    this.logging.emit(
      this.category,
      WebDNNLogging.FATAL,
      message,
      optionalParams
    );
  }
}

interface WebDNNLoggingAdapter {
  emit(
    category: string,
    severity: number,
    message: any,
    optionalParams: any[]
  ): void;

  clear(): void;
}

class WebDNNLoggingAdapterConsole implements WebDNNLoggingAdapter {
  emit(
    category: string,
    severity: number,
    message: any,
    optionalParams: any[]
  ): void {
    const messageWithCategory = `${category}: ${message}`;
    switch (severity) {
      case WebDNNLogging.FATAL:
        console.error(messageWithCategory, ...optionalParams);
        break;
      case WebDNNLogging.ERROR:
        console.error(messageWithCategory, ...optionalParams);
        break;
      case WebDNNLogging.WARN:
        console.warn(messageWithCategory, ...optionalParams);
        break;
      case WebDNNLogging.INFO:
        console.info(messageWithCategory, ...optionalParams);
        break;
      case WebDNNLogging.DEBUG:
        console.debug(messageWithCategory, ...optionalParams);
        break;
    }
  }

  // eslint-disable-next-line @typescript-eslint/no-empty-function
  clear(): void {}
}

class WebDNNLoggingAdapterFile implements WebDNNLoggingAdapter {
  buffer: {
    category: string;
    severity: number;
    message: any;
    optionalParams: any[];
  }[];
  constructor() {
    this.buffer = [];
  }

  emit(
    category: string,
    severity: number,
    message: any,
    optionalParams: any[]
  ): void {
    this.buffer.push({ category, severity, message, optionalParams });
  }

  clear(): void {
    this.buffer = [];
  }

  saveToLocalFile(): void {
    const content: string[] = this.buffer.map(
      (item) => JSON.stringify(item) + "\n"
    );
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob(content, { type: "text/plain" }));
    a.download = "logging.log";

    a.style.display = "none";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  }
}

interface WebDNNLoggingConfigAdapter {
  adapter: string;
  adapterParams?: unknown[];
  loglevel?: Record<string, number>;
}

interface WebDNNLoggingConfig {
  adapters: Record<string, WebDNNLoggingConfigAdapter>;
}

export class WebDNNLogging {
  static readonly FATAL = 0;
  static readonly ERROR = 1;
  static readonly WARN = 2;
  static readonly INFO = 3;
  static readonly DEBUG = 4;

  adapters: Record<string, WebDNNLoggingAdapter>;
  adapterFactories: Record<string, (...params: any[]) => WebDNNLoggingAdapter>;
  currentConfig!: WebDNNLoggingConfig;

  constructor() {
    this.adapters = {};
    this.adapterFactories = {
      console: () => new WebDNNLoggingAdapterConsole(),
      file: () => new WebDNNLoggingAdapterFile(),
    };
    this.config({
      adapters: {
        console: {
          adapter: "console",
          loglevel: {
            "": WebDNNLogging.WARN,
          },
        },
      },
    });
  }

  config(config: WebDNNLoggingConfig): void {
    // generate adapters
    this.currentConfig = config;
    const adapters = config.adapters;
    this.adapters = {};
    for (const key of Object.keys(adapters)) {
      const ad = adapters[key];
      const factory = this.adapterFactories[ad.adapter];
      if (!factory) {
        console.error(`Logging adapter ${ad.adapter} not found.`);
        continue;
      }
      try {
        const adinstance = factory(...(ad.adapterParams || []));
        this.adapters[key] = adinstance;
      } catch {
        console.error(`Logging adapter ${ad.adapter} constructor error.`);
        continue;
      }
    }
  }

  static getInstance(): WebDNNLogging {
    return window.WebDNNLoggingManagerInstance;
  }

  static getLogger(category: string, logging?: WebDNNLogging): WebDNNLogger {
    if (!logging) {
      logging = WebDNNLogging.getInstance();
    }
    return new WebDNNLogger(category, logging);
  }

  emit(
    category: string,
    severity: number,
    message: any,
    optionalParams: any[]
  ): void {
    for (const key of Object.keys(this.adapters)) {
      // TODO: filter by category
      const ad = this.adapters[key];
      const config = this.currentConfig.adapters[key];
      let match = true;
      const ll = config.loglevel;
      if (ll) {
        const rootLoglevel = ll[""];
        if (rootLoglevel !== undefined) {
          if (severity >= rootLoglevel) {
            // high severity value = unimportant
            match = false;
          }
        }
      }
      if (match) {
        ad.emit(category, severity, message, optionalParams);
      }
    }
  }

  /**
   * Clear buffered messages
   */
  clear(): void {
    for (const key of Object.keys(this.adapters)) {
      const ad = this.adapters[key];
      ad.clear();
    }
  }
}

if (typeof window.WebDNNLoggingManagerInstance === "undefined") {
  window.WebDNNLoggingManagerInstance = new WebDNNLogging();
}
