import "../style/index.scss";
import "./modules/analytics.js";
const DENSITY = 5000;
const MIN_VX = 0.1;
const MIN_VY = 0.1;
const MAX_VX = 0.3;
const MAX_VY = 0.3;
const PROXIMITY = 100;
const DOT_COLOR = 'rgba(214, 230, 255, 1)';
const LINE_COLOR = 'rgba(214, 230, 255, 0.4)';
const LINE_WIDTH = 0.5;
const RADIUS_HALF = 2;
const PI2 = Math.PI * 2;

interface Particle {
    x: number;
    y: number;
    vx: number;
    vy: number;
}

class ParticleGround {
    container: HTMLElement;
    ctx: CanvasRenderingContext2D;
    canvas: HTMLCanvasElement;
    particles: Particle[] = [];

    constructor(container: HTMLElement) {
        this.container = container;
        this.canvas = document.createElement('canvas');
        this.canvas.width = this.container.offsetWidth;
        this.canvas.height = this.container.offsetHeight;
        this.canvas.style.display = 'block';

        this.container.insertBefore(this.canvas, this.container.firstChild);

        let ctx = this.canvas.getContext('2d');
        if (!ctx) throw Error('Canvas Initialization Failed.');
        this.ctx = ctx;
        this.ctx.fillStyle = DOT_COLOR;
        this.ctx.strokeStyle = LINE_COLOR;
        this.ctx.lineWidth = LINE_WIDTH;

        let numParticles = Math.round((this.canvas.width * this.canvas.height) / DENSITY);
        for (let i = 0; i < numParticles; i++) {
            this.particles.push({
                x: Math.ceil(Math.random() * this.canvas.width),
                y: Math.ceil(Math.random() * this.canvas.height),
                vx: ((MAX_VX - MIN_VX) * Math.random() + MIN_VX) * (Math.random() >= 0.5 ? +1 : -1),
                vy: ((MAX_VY - MIN_VY) * Math.random() + MIN_VY) * (Math.random() >= 0.5 ? +1 : -1),
            });
        }

        window.addEventListener('resize', () => this.resizeHandler());

        this.update();
    }

    update() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        let containerWidth = this.container.offsetWidth;
        let containerHeight = this.container.offsetHeight;
        for (let i = 0; i < this.particles.length; i++) {
            let p = this.particles[i];

            if (p.x + p.vx > containerWidth || p.x + p.vx < 0) p.vx = -p.vx;
            if (p.y + p.vy > containerHeight || p.y + p.vy < 0) p.vy = -p.vy;

            p.x += p.vx;
            p.y += p.vy;
        }

        for (let i = 0; i < this.particles.length; i++) {
            let p1 = this.particles[i];

            this.ctx.beginPath();
            this.ctx.arc(p1.x, p1.y, RADIUS_HALF, 0, PI2, true);
            this.ctx.closePath();
            this.ctx.fill();

            this.ctx.beginPath();
            for (let j = i; j < this.particles.length; j++) {
                let p2 = this.particles[j];

                let dx = p1.x - p2.x;
                let dy = p2.y - p2.y;

                if (Math.sqrt((dx * dx) + (dy * dy)) < PROXIMITY) {
                    this.ctx.moveTo(p1.x, p1.y);
                    this.ctx.lineTo(p2.x, p2.y);
                }
            }
            this.ctx.stroke();
            this.ctx.closePath();
        }

        requestAnimationFrame(() => this.update());
    }

    resizeHandler() {
        let containerWidth = this.canvas.width = this.container.offsetWidth;
        let containerHeight = this.canvas.height = this.container.offsetHeight;
        this.ctx.fillStyle = DOT_COLOR;
        this.ctx.strokeStyle = LINE_COLOR;
        this.ctx.lineWidth = LINE_WIDTH;

        for (let i = this.particles.length - 1; i >= 0; i--) {
            if (this.particles[i].x > containerWidth || this.particles[i].y > containerHeight) {
                this.particles.splice(i, 1);
            }
        }

        let numParticles = Math.round((this.canvas.width * this.canvas.height) / DENSITY);
        while (this.particles.length < numParticles) {
            this.particles.push({
                x: Math.ceil(Math.random() * this.canvas.width),
                y: Math.ceil(Math.random() * this.canvas.height),
                vx: ((MAX_VX - MIN_VX) * Math.random() + MIN_VX) * (Math.random() >= 0.5 ? +1 : -1),
                vy: ((MAX_VY - MIN_VY) * Math.random() + MIN_VY) * (Math.random() >= 0.5 ? +1 : -1),
            });
        }
        if (this.particles.length > numParticles) {
            this.particles.splice(numParticles);
        }
    }
}

window.onload = () => {
    let availability: { [key: string]: boolean } = {
        'webgpu': ('WebGPUComputeCommandEncoder' in window),
        'webassembly': ('Worker' in window),
        'fallback': true
    };

    for (let backend of ['webgpu', 'webassembly', 'fallback']) {
        let nodes = document.querySelectorAll(`.Compatibility-ThisBrowserTable .Compatibility-${backend}`)
        for (let i = 0; i < nodes.length; i++) {
            let node = nodes[i] as HTMLElement;
            node.classList.remove('Compatibility-checking');
            let statusNode = node.querySelector('.Compatibility-Status');

            if (availability[backend]) {
                node.classList.add('Compatibility-supported');
                node.classList.remove('Compatibility-not_supported');
                if (statusNode) statusNode.textContent = 'Supported';
            } else {
                node.classList.remove('Compatibility-supported');
                node.classList.add('Compatibility-not_supported');
                if (statusNode) statusNode.textContent = 'Not supported';
            }
        }
    }

    let IS_ES2017 = true;
    try {
        eval('(() => { async function test(){return Promise.resolve()} })();');
    } catch (e) {
        IS_ES2017 = false;
    }

    let iframes = document.querySelectorAll('iframe');
    for (let i = 0; i < iframes.length; i++) {
        let iframe = iframes[i];
        let baseUrl = iframe.dataset['src'];
        if (!baseUrl) throw Error('baseUrl is not found');
        iframe.src = IS_ES2017 ? baseUrl : baseUrl.replace('.html', '.es5.html');
    }

    let splash = document.getElementById('splash');
    if (!splash) throw Error('#splash is not found.');
    new ParticleGround(splash);

    if ('serviceWorker' in navigator) navigator.serviceWorker.register('/webdnn/sw.js');
};
