attribute vec4 a_Position;
attribute vec4 a_Color;
attribute vec4 a_Normal;

uniform mat4 u_Model;
uniform mat4 u_View;
uniform mat4 u_Projection;

uniform vec3 u_LightPosition;
uniform vec3 u_LightDirection;

varying vec4 v_Color;
varying vec4 v_Normal;
varying vec3 v_LightDirection;

void main() {
    gl_Position = u_Projection * u_View * u_Model * a_Position;
    v_Color = a_Color;
    v_Normal = u_Projection * u_View * u_Model * a_Normal;
    v_LightDirection = (u_Projection * u_View * u_Model * vec4(u_LightDirection, 0)).xyz;
}
