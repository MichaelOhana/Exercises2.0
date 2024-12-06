import React from 'react';
import styles from './Templates.module.css';

const LessonTemplate = ({ lesson }) => {
  return (
    <div className={styles.template}>
      <h1>{lesson.title}</h1>
      <div className={styles.content}>
        <section className={styles.introduction}>
          <h2>Introduction</h2>
          <p>Lesson introduction goes here...</p>
        </section>
        
        <section className={styles.mainContent}>
          <h2>Main Content</h2>
          <p>Main lesson content goes here...</p>
        </section>
        
        <section className={styles.summary}>
          <h2>Summary</h2>
          <p>Lesson summary goes here...</p>
        </section>
      </div>
      
      <button className={styles.nextButton}>Next Lesson</button>
    </div>
  );
};

export default LessonTemplate; 