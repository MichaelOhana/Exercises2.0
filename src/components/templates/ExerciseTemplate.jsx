import React from 'react';
import styles from './Templates.module.css';

const ExerciseTemplate = ({ exercise }) => {
  return (
    <div className={styles.template}>
      <h1>{exercise.title}</h1>
      <div className={styles.content}>
        <section>
          <h2>Instructions</h2>
          <p>Exercise instructions go here...</p>
        </section>
        
        <section>
          <h2>Your Task</h2>
          <p>Exercise content goes here...</p>
        </section>
      </div>
      
      <button className={styles.nextButton}>Next Exercise</button>
    </div>
  );
};

export default ExerciseTemplate; 