import { Canvas } from "@react-three/fiber";
import { useState } from "react";
import { useSpring, animated } from "@react-spring/three";
import { OrbitControls, useTexture } from "@react-three/drei";
import card from "./assets/card.webp";
import card2 from "./assets/card2.webp";
import card3 from "./assets/card3.webp";
import cardback from "./assets/back.png"

const cards = [
  { id: 1, image: card },
  { id: 2, image: card2 },
  { id: 3, image: card3 },
  { id: 4, image: card },
  { id: 5, image: card2 },
  { id: 6, image: card3 },
  { id: 7, image: card3 },
];
import "./App.css";

function Card({ image, setSelectedCard }) {
  return (
    <div className="cursor-pointer" onClick={() => setSelectedCard(image)}>
      <img
        src={image}
        alt="Card"
        className="w-48  shadow-md transition-transform hover:scale-105"
      />
    </div>
  );
}

function Card3D({ image }) {
  const frontTexture = useTexture(image);
  const backTexture = useTexture(cardback);
  const [{ rotation }, setRotation] = useSpring(() => ({ rotation: [0, 0, 0], config: { mass: 20, tension: 300, friction: 100 } }));

  return (
    <animated.group
      onPointerMove={(e) => {
        const { offsetX, offsetY } = e.nativeEvent;
        const x = (offsetX / window.innerWidth - 0.5) * 0.6;
        const y = (offsetY / window.innerHeight - 0.5) * 0.6;
        setRotation({ rotation: [-y, x, 0] });
      }}
      onPointerLeave={() => setRotation({ rotation: [0, 0, 0] })}
      rotation={rotation}
    >
      {/* Front Side */}
      <mesh position={[0, 0, 0]}>
        <planeGeometry args={[2.5, 3.5]} />
        <meshStandardMaterial map={frontTexture} />
      </mesh>
      {/* Back Side */}
      <mesh rotation={[0, Math.PI, 0]}>
        <planeGeometry args={[2.5, 3.5]} />
        <meshStandardMaterial map={backTexture} />
      </mesh>
    </animated.group>
  );
}

function CardViewer({ image, setSelectedCard }) {
  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-80">
      <div className="relative w-[500px] h-[600px] flex flex-col items-center justify-center">
        <Canvas className="w-full h-[500px]" camera={{ position: [0, 0, 3.3] }}>
          <ambientLight intensity={0.5} />
          <directionalLight position={[2, 2, 5]} intensity={1} />
          <OrbitControls enableZoom={false} enablePan={false} />
          <Card3D image={image} />
        </Canvas>
        <button
          onClick={() => setSelectedCard(null)}
          className="bg-red-500 hover:bg-red-400 text-white font-bold py-2 px-4 border-b-4 border-red-700 hover:border-red-500 rounded"
        >
          Close
        </button>
      </div>
    </div>
  );
}

function App() {
  const [selectedCard, setSelectedCard] = useState(null);

  return (
    <div className="flex flex-col items-center justify-center bg-gray-900 p-4">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {cards.map((card) => (
          <Card key={card.id} image={card.image} setSelectedCard={setSelectedCard} />
        ))}
      </div>
      {selectedCard && <CardViewer image={selectedCard} setSelectedCard={setSelectedCard} />}
    </div>
  );
}

export default App;
