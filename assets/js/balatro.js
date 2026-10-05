// Shader by localthunk (https://www.playbalatro.com), via https://www.shadertoy.com/view/XXtBRr

(function () {
    const VERT = `
attribute vec2 a_position;
void main() { gl_Position = vec4(a_position, 0.0, 1.0); }
`;

    const FRAG = `
precision highp float;

uniform vec2 iResolution;
uniform float iTime;

#define SPIN_ROTATION 0.2
#define SPIN_SPEED 3.0
#define OFFSET vec2(0.0, 0.0)
#define COLOUR_1 vec4(0.055, 0.053, 0.053, 1.0)
#define COLOUR_2 vec4(0.030, 0.030, 0.030, 1.0)
#define COLOUR_3 vec4(0.200, 0.200, 0.200, 1.0)
#define CONTRAST 1.2
#define SPIN_AMOUNT 0.5
#define PIXEL_FILTER 400.0
#define SPIN_EASE 0.5
#define PI 3.14159265359
#define IS_ROTATE true

#define ACCENT_1 vec4(1.00, 0.30, 0.22, 1.0)
#define ACCENT_2 vec4(0.35, 0.60, 1.00, 1.0)
#define ACCENT_3 vec4(0.70, 0.15, 1.00, 1.0)
#define ACCENT_POS_1 0.35
#define ACCENT_POS_2 0.50
#define ACCENT_POS_3 0.65
#define ACCENT_STRENGTH 0.90
#define ACCENT_SHARP_1 64.0
#define ACCENT_SHARP_2 48.0
#define ACCENT_SHARP_3 256.0
#define ACCENT_LO 0.30
#define ACCENT_HI 0.70
#define FRAG_FREQ 0.9
#define FRAG_SHARP 10.0

float streak(float x, float centre, float width, float sharpness) {
    return pow(max(0., 1. - width*abs(centre - x)), sharpness);
}

vec4 effect(vec2 screenSize, vec2 screen_coords) {
    float pixel_size = length(screenSize.xy) / PIXEL_FILTER;
    vec2 uv = (floor(screen_coords.xy*(1./pixel_size))*pixel_size - 0.5*screenSize.xy)/length(screenSize.xy) - OFFSET;
    float uv_len = length(uv);

    float speed = (SPIN_ROTATION*SPIN_EASE*0.2);
    if(IS_ROTATE){
       speed = iTime * speed;
    }
    speed += 302.2;
    float new_pixel_angle = atan(uv.y, uv.x) + speed - SPIN_EASE*20.*(1.*SPIN_AMOUNT*uv_len + (1. - 1.*SPIN_AMOUNT));
    vec2 mid = (screenSize.xy/length(screenSize.xy))/2.;
    uv = (vec2((uv_len * cos(new_pixel_angle) + mid.x), (uv_len * sin(new_pixel_angle) + mid.y)) - mid);

    uv *= 30.;
    speed = iTime*(SPIN_SPEED);
    vec2 uv2 = vec2(uv.x+uv.y);

    for(int i=0; i < 5; i++) {
        uv2 += sin(max(uv.x, uv.y)) + uv;
        uv  += 0.5*vec2(cos(5.1123314 + 0.353*uv2.y + speed*0.131121),sin(uv2.x - 0.113*speed));
        uv  -= 1.0*cos(uv.x + uv.y) - 1.0*sin(uv.x*0.711 - uv.y);
    }

    float contrast_mod = (0.25*CONTRAST + 0.5*SPIN_AMOUNT + 1.2);
    float paint_res = min(2., max(0.,length(uv)*(0.035)*contrast_mod));
    float c1p = max(0.,1. - contrast_mod*abs(1.-paint_res));
    float c2p = max(0.,1. - contrast_mod*abs(paint_res));
    float c3p = 1. - min(1., c1p + c2p);
    float frag = pow(max(0., sin(uv.x*FRAG_FREQ + uv.y*FRAG_FREQ*0.7)), FRAG_SHARP);
    float band = streak(paint_res, ACCENT_POS_1, contrast_mod, ACCENT_SHARP_1)
               + streak(paint_res, ACCENT_POS_2, contrast_mod, ACCENT_SHARP_2)
               + streak(paint_res, ACCENT_POS_3, contrast_mod, ACCENT_SHARP_3);
    float h = clamp((paint_res - ACCENT_LO)/(ACCENT_HI - ACCENT_LO), 0., 1.);
    vec3 hue = mix(ACCENT_1.rgb, ACCENT_2.rgb, smoothstep(0., 0.5, h));
    hue = mix(hue, ACCENT_3.rgb, smoothstep(0.5, 1., h));
    vec3 accent = hue * band * frag;
    return (0.3/CONTRAST)*COLOUR_1 + (1. - 0.3/CONTRAST)*(COLOUR_1*c1p + COLOUR_2*c2p + vec4(c3p*COLOUR_3.rgb, c3p*COLOUR_1.a)) + vec4(ACCENT_STRENGTH*accent, 0.0);
}

void main() {
    gl_FragColor = effect(iResolution.xy, gl_FragCoord.xy);
}
`;

    const canvas = document.createElement("canvas");
    Object.assign(canvas.style, {
        position: "fixed",
        top: "0",
        left: "0",
        width: "100%",
        height: "100%",
        zIndex: "-1",
        opacity: "0.75",
        pointerEvents: "none"
    });
    document.body.appendChild(canvas);

    const gl = canvas.getContext("webgl");
    if (!gl) {
        console.error("balatro: WebGL not supported.");
        return;
    }

    const compile = (type, src) => {
        const s = gl.createShader(type);
        gl.shaderSource(s, src);
        gl.compileShader(s);
        if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) {
            console.error("balatro:", gl.getShaderInfoLog(s));
        }
        return s;
    };

    const program = gl.createProgram();
    gl.attachShader(program, compile(gl.VERTEX_SHADER, VERT));
    gl.attachShader(program, compile(gl.FRAGMENT_SHADER, FRAG));
    gl.linkProgram(program);
    gl.useProgram(program);

    gl.bindBuffer(gl.ARRAY_BUFFER, gl.createBuffer());
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1,-1, 1,-1, -1,1, -1,1, 1,-1, 1,1]), gl.STATIC_DRAW);

    const position = gl.getAttribLocation(program, "a_position");
    gl.enableVertexAttribArray(position);
    gl.vertexAttribPointer(position, 2, gl.FLOAT, false, 0, 0);

    const uResolution = gl.getUniformLocation(program, "iResolution");
    const uTime = gl.getUniformLocation(program, "iTime");

    const resize = () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        gl.viewport(0, 0, canvas.width, canvas.height);
    };
    window.addEventListener("resize", resize);
    resize();

    const render = (t) => {
        gl.uniform2f(uResolution, canvas.width, canvas.height);
        gl.uniform1f(uTime, t * 0.001);
        gl.drawArrays(gl.TRIANGLES, 0, 6);
        requestAnimationFrame(render);
    };
    requestAnimationFrame(render);
})();
