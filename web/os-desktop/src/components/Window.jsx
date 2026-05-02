import React, { useState, useRef, useEffect } from 'react';

export default function Window({ id, title, icon, children, initialPos, initialSize, onClose, onMinimize, onFocus, zIndex }) {
  const [pos, setPos] = useState(initialPos || { x: 80, y: 60 });
  const [size, setSize] = useState(initialSize || { w: 700, h: 480 });
  const [maximized, setMaximized] = useState(false);
  const prevState = useRef({ pos, size });

  const handleMouseDown = (e) => {
    if (maximized) return;
    onFocus?.(id);
    const startX = e.clientX - pos.x;
    const startY = e.clientY - pos.y;
    const onMove = (ev) => setPos({ x: ev.clientX - startX, y: Math.max(0, ev.clientY - startY) });
    const onUp = () => { document.removeEventListener('mousemove', onMove); document.removeEventListener('mouseup', onUp); };
    document.addEventListener('mousemove', onMove);
    document.addEventListener('mouseup', onUp);
  };

  const toggleMaximize = () => {
    if (maximized) {
      setPos(prevState.current.pos);
      setSize(prevState.current.size);
    } else {
      prevState.current = { pos, size };
      setPos({ x: 0, y: 0 });
      setSize({ w: window.innerWidth, h: window.innerHeight - 48 });
    }
    setMaximized(!maximized);
  };

  return (
    <div
      className="window"
      style={{
        left: pos.x, top: pos.y,
        width: size.w, height: size.h,
        zIndex: zIndex || 100,
      }}
      onMouseDown={() => onFocus?.(id)}
    >
      <div className="window-titlebar" onMouseDown={handleMouseDown} onDoubleClick={toggleMaximize}>
        <div className="window-dots">
          <button className="window-dot close" onClick={() => onClose?.(id)} />
          <button className="window-dot minimize" onClick={() => onMinimize?.(id)} />
          <button className="window-dot maximize" onClick={toggleMaximize} />
        </div>
        <span className="window-title">{icon} {title}</span>
        <div style={{ width: 54 }} />
      </div>
      <div className="window-body">
        {children}
      </div>
    </div>
  );
}
