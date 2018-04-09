varying vec2 v_UV;

uniform vec3 u_Color;
uniform sampler2D u_TextureSampler;

void main() {
    gl_FragColor = vec4(u_Color, texture2D(u_TextureSampler, v_UV).w);
}
