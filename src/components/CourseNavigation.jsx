import React from 'react';
import styles from './CourseNavigation.module.css';

const CourseNavigation = ({ isOpen, onToggle, onContentSelect }) => {
  // Example course structure
  const courseStructure = {
    units: [
      {
        id: 1,
        title: 'Unit 1: Introduction',
        content: [
          { id: 'l1', type: 'lesson', title: 'Getting Started' },
          { id: 'e1', type: 'exercise', title: 'First Exercise' },
          { id: 'q1', type: 'quiz', title: 'Unit 1 Quiz' },
        ],
      },
      // Add more units as needed
    ],
  };

  return (
    <div className={`${styles.navigation} ${isOpen ? styles.open : styles.closed}`}>
      <div className={styles.content}>
        {courseStructure.units.map((unit) => (
          <div key={unit.id} className={styles.unit}>
            <h3>{unit.title}</h3>
            <div className={styles.unitContent}>
              {unit.content.map((item) => (
                <div
                  key={item.id}
                  className={styles.contentItem}
                  onClick={() => onContentSelect(item)}
                >
                  {item.title}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
      <button className={styles.toggleButton} onClick={onToggle}>
        {isOpen ? '←' : '→'}
      </button>
    </div>
  );
};

export default CourseNavigation; 