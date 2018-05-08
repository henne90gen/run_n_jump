attribute vec3 a_Position;

uniform mat4 u_Model;
uniform mat4 u_View;
uniform mat4 u_Projection;

void main() {
    mat4 ModelViewProjection = u_Projection * u_View * u_Model;
    gl_Position = ModelViewProjection * vec4(a_Position, 1);
}
