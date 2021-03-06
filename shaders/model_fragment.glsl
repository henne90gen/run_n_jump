struct light {
    vec3 position;
    vec3 color;
    float power;
};

varying vec3 v_Normal;
varying vec3 v_LightDirection;
varying vec3 v_WorldPosition;
varying vec3 v_EyeDirection;

uniform mat4 u_Model;
uniform mat4 u_View;
uniform mat4 u_Projection;
uniform vec3 u_Color;

uniform light u_Lights[LIGHTS];

void main() {
	// Material properties
	vec3 MaterialDiffuseColor = u_Color.rgb;
	vec3 MaterialAmbientColor = vec3(0.15, 0.15, 0.15) * MaterialDiffuseColor;
	vec3 MaterialSpecularColor = vec3(0.3, 0.3, 0.3);

    // Ambient : simulates indirect lighting
    vec3 color = MaterialAmbientColor;


    for (int i = 0; i < LIGHTS; i++) {
        // Distance to the light
        float distance = length(u_Lights[i].position - v_WorldPosition);

        // Normal of the computed fragment, in camera space
        vec3 n = normalize(v_Normal);
        // Direction of the light (from the fragment to the light)
        vec3 l = normalize(v_LightDirection);
        // Cosine of the angle between the normal and the light direction,
        // clamped above 0
        //  - light is at the vertical of the triangle -> 1
        //  - light is perpendicular to the triangle -> 0
        //  - light is behind the triangle -> 0
        float cosTheta = clamp(dot(n, l), 0.0, 1.0);

        // Eye vector (towards the camera)
        vec3 E = normalize(v_EyeDirection);
        // Direction in which the triangle reflects the light
        vec3 R = reflect(-l,n);
        // Cosine of the angle between the Eye vector and the Reflect vector,
        // clamped to 0
        //  - Looking into the reflection -> 1
        //  - Looking elsewhere -> < 1
        float cosAlpha = clamp(dot(E, R), 0.0, 1.0);

        color =
            color +
            // Diffuse : "color" of the object
            MaterialDiffuseColor * u_Lights[i].color * u_Lights[i].power * cosTheta / (distance * distance) +
            // Specular : reflective highlight, like a mirror
            MaterialSpecularColor * u_Lights[i].color * u_Lights[i].power * pow(cosAlpha, 5.0) / (distance*distance);
    }

    gl_FragColor = vec4(color, 1.0);
}
