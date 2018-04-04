attribute vec4 a_Position;
attribute vec4 a_Color;
attribute vec4 a_Normal;

uniform vec3 u_LightPosition;
uniform vec3 u_LightDirection;

varying vec4 v_Color;
varying vec4 v_Normal;
varying vec3 v_LightDirection;

void main() {
    gl_Position = gl_ModelViewProjectionMatrix * a_Position;
    v_Color = a_Color;
    v_Normal = gl_ModelViewProjectionMatrix * a_Normal;
    v_LightDirection = (gl_ModelViewProjectionMatrix * vec4(u_LightDirection, 0)).xyz;
}
