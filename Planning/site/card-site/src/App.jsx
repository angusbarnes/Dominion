import { useState } from "react";
import { motion } from "framer-motion";

const cards = [
  { id: 1, image: "https://via.placeholder.com/200x300" },
  { id: 2, image: "https://via.placeholder.com/200x300" },
  { id: 3, image: "https://via.placeholder.com/200x300" },
  { id: 4, image: "https://via.placeholder.com/200x300" },
];
import "./App.css";

function App() {
  const [selectedCard, setSelectedCard] = useState(null);
  const [tilt, setTilt] = useState({ x: 0, y: 0 });

  const handleMouseMove = (e) => {
    const { innerWidth, innerHeight } = window;
    const x = (e.clientX / innerWidth - 0.5) * 20;
    const y = (e.clientY / innerHeight - 0.5) * 20;
    setTilt({ x, y });
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-900 p-4">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {cards.map((card) => (
          <div
            key={card.id}
            className="w-48 h-72 bg-gray-700 rounded-xl flex items-center justify-center cursor-pointer overflow-hidden"
            onClick={() => setSelectedCard(card)}
          >
            <img src={card.image} alt="Card" className="w-full h-full object-cover" />
          </div>
        ))}
      </div>

      {selectedCard && (
        <div
          className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50"
          onClick={() => setSelectedCard(null)}
        >
          <motion.div
            className="w-64 h-96 bg-gray-800 rounded-xl shadow-lg overflow-hidden"
            style={{ perspective: 1000 }}
            onMouseMove={handleMouseMove}
            onMouseLeave={() => setTilt({ x: 0, y: 0 })}
            animate={{ rotateX: tilt.y, rotateY: -tilt.x }}
            transition={{ type: "spring", stiffness: 100, damping: 10 }}
          >
            <img src={selectedCard.image} alt="Card" className="w-full h-full object-cover" />
          </motion.div>
        </div>
      )}
    </div>
  );
}

export default App;
